import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import main
from app.utils import match_citation_to_chunk
from tests.fixtures import isolated_backend, make_pdf


class NotebookApiTests(unittest.TestCase):
    def setUp(self):
        directory = self.enterContext(TemporaryDirectory(prefix="notemind-api-"))
        self.directory = Path(directory)
        self.collection, self.completions = self.enterContext(isolated_backend(self.directory))
        self.client = self.enterContext(TestClient(main.app))

    def upload(self, filename="research.pdf", pages=None):
        pdf = make_pdf(pages or ["Qubits use superposition.", "Error correction protects quantum information."])
        response = self.client.post("/upload", files={"file": (filename, pdf, "application/pdf")})
        self.assertEqual(response.status_code, 200, response.text)
        return pdf, response

    def test_upload_keeps_page_boundaries_and_pdf_can_be_read(self):
        pdf, response = self.upload("Research Notes.PDF")
        self.assertEqual(response.json()["chunks_count"], 2)
        self.assertEqual(self.client.get("/files").json(), {"files": ["Research Notes.PDF"]})
        chunks = list(self.collection.chunks.values())
        self.assertEqual([chunk["metadata"]["page"] for chunk in chunks], [1, 2])
        self.assertTrue(all(chunk["metadata"]["source"] == "Research Notes.PDF" for chunk in chunks))
        self.assertTrue(all(chunk["metadata"]["chunk_id"] == chunk["id"] for chunk in chunks))
        self.assertNotIn("Error correction", chunks[0]["text"])
        served = self.client.get("/files/Research%20Notes.PDF")
        self.assertEqual(served.content, pdf)
        self.assertEqual(served.headers["content-type"], "application/pdf")
        self.assertIn("inline", served.headers["content-disposition"])
        partial = self.client.get("/files/Research%20Notes.PDF", headers={"Range": "bytes=0-4"})
        self.assertEqual(partial.status_code, 206)
        self.assertEqual(partial.content, b"%PDF-")

    def test_invalid_replacement_keeps_existing_source(self):
        pdf, _ = self.upload()
        chunks = dict(self.collection.chunks)
        response = self.client.post("/upload", files={"file": ("research.pdf", make_pdf([""]), "application/pdf")})
        self.assertEqual(response.status_code, 400)
        self.assertEqual((self.directory / "research.pdf").read_bytes(), pdf)
        self.assertEqual(self.collection.chunks, chunks)
        self.assertEqual(list(self.directory.iterdir()), [self.directory / "research.pdf"])

    def test_embedding_failure_keeps_existing_source(self):
        pdf, _ = self.upload()
        chunks = dict(self.collection.chunks)
        with patch.object(main, "get_embeddings_batch", side_effect=RuntimeError("Embedding provider unavailable")):
            response = self.client.post("/upload", files={"file": ("research.pdf", make_pdf(["New research."]), "application/pdf")})
        self.assertEqual(response.status_code, 500)
        self.assertEqual((self.directory / "research.pdf").read_bytes(), pdf)
        self.assertEqual(self.collection.chunks, chunks)

    def test_index_failure_keeps_existing_source(self):
        pdf, _ = self.upload()
        chunks = dict(self.collection.chunks)
        with patch.object(self.collection, "upsert", side_effect=RuntimeError("Index unavailable")):
            response = self.client.post("/upload", files={"file": ("research.pdf", make_pdf(["New research."]), "application/pdf")})
        self.assertEqual(response.status_code, 500)
        self.assertEqual((self.directory / "research.pdf").read_bytes(), pdf)
        self.assertEqual(self.collection.chunks, chunks)

    def test_replacement_removes_stale_chunks_after_indexing(self):
        self.upload()
        pdf, _ = self.upload(pages=["Replacement research has one page."])
        self.assertEqual(len(self.collection.chunks), 1)
        self.assertEqual((self.directory / "research.pdf").read_bytes(), pdf)
        self.assertEqual(self.collection.get()["documents"], ["Replacement research has one page."])

    def test_single_source_query_excludes_other_notebooks(self):
        self.upload("a.pdf", ["Alpha particles are studied here."])
        self.upload("private.pdf", ["Unrelated notebook secret."])
        self.collection.filters.clear()
        response = self.client.post("/query", data={"query": "What is studied?", "filename": "a.pdf"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn("secret", response.json()["answer"])
        self.assertEqual({citation["filename"] for citation in response.json()["citations"]}, {"a.pdf"})
        self.assertEqual(self.collection.filters, [{"source": "a.pdf"}, {"source": "a.pdf"}])

    def test_repeated_source_fields_scope_sparse_and_dense_retrieval(self):
        self.upload("a.pdf", ["Alpha particles are studied here."])
        self.upload("b.pdf", ["Beta particles have another source."])
        self.upload("private.pdf", ["Unrelated notebook secret."])
        self.collection.filters.clear()
        response = self.client.post("/query", data={"query": "Summarize particles", "filenames": ["a.pdf", "b.pdf", "a.pdf"]})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertNotIn("secret", response.json()["answer"])
        self.assertEqual({citation["filename"] for citation in response.json()["citations"]}, {"a.pdf", "b.pdf"})
        self.assertEqual(self.collection.filters, [{"source": {"$in": ["a.pdf", "b.pdf"]}}] * 2)

    def test_legacy_unscoped_query_still_searches_all_sources(self):
        self.upload("a.pdf", ["Alpha source content."])
        self.upload("b.pdf", ["Beta source content."])
        self.collection.filters.clear()
        response = self.client.post("/query", data={"query": "Summarize sources"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual({citation["filename"] for citation in response.json()["citations"]}, {"a.pdf", "b.pdf"})
        self.assertEqual(self.collection.filters, [None, None])

    def test_citation_metadata_comes_from_the_matching_chunk(self):
        self.upload()
        self.completions.create = lambda **kwargs: main.AnswerResponse(answer="Information is protected.", citations=[
            main.Citation(sentence="Error correction protects quantum information.", filename="wrong.pdf", page=99),
        ])
        response = self.client.post("/query", data={"query": "How is information protected?", "filename": "research.pdf"})
        self.assertEqual(response.json()["citations"], [{
            "sentence": "Error correction protects quantum information.", "filename": "research.pdf", "page": 2,
        }])

    def test_no_sources_error_preserves_400_status(self):
        response = self.client.post("/query", data={"query": "Question", "filename": "missing.pdf"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("No documents indexed", response.json()["detail"])

    def test_invalid_requests_fail_before_retrieval(self):
        for data in [
            {"query": "   "},
            {"query": "Question", "filename": "a.pdf", "filenames": ["b.pdf"]},
            {"query": "Question", "filenames": [""]},
            {"query": "Question", "filename": "..\\private.pdf"},
        ]:
            with self.subTest(data=data):
                self.assertEqual(self.client.post("/query", data=data).status_code, 400)
        self.assertEqual(self.collection.filters, [])
        self.assertEqual(self.client.post("/query", json={"query": "JSON is not form data"}).status_code, 422)

    def test_unsupported_upload_and_missing_pdf_keep_client_status_codes(self):
        response = self.client.post("/upload", files={"file": ("notes.txt", b"Text", "text/plain")})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get("/files/missing.pdf").status_code, 404)
        self.assertEqual(self.client.get("/files/notes.txt").status_code, 400)
        self.assertEqual(self.client.get("/files/..%5Cprivate.pdf").status_code, 400)


class CitationMatchingTests(unittest.TestCase):
    def test_exact_sentence_wins_over_incorrect_model_metadata(self):
        chunks = [
            {"text": "Alpha and beta particles differ greatly.", "metadata": {"source": "wrong.pdf", "page": 9}},
            {"text": "Alpha and beta particles.", "metadata": {"source": "right.pdf", "page": 2}},
        ]
        chunk, sentence = match_citation_to_chunk(chunks, "Alpha and beta particles.", "wrong.pdf", 9)
        self.assertEqual(chunk["metadata"], {"source": "right.pdf", "page": 2})
        self.assertEqual(sentence, "Alpha and beta particles.")

    def test_equal_passages_use_source_and_page_to_break_ties(self):
        chunks = [
            {"text": "A shared passage.", "metadata": {"source": "a.pdf", "page": 1}},
            {"text": "A shared passage.", "metadata": {"source": "b.pdf", "page": 2}},
        ]
        self.assertEqual(match_citation_to_chunk(chunks, "A shared passage.", "b.pdf", 2)[0], chunks[1])

    def test_unmatched_citation_does_not_invent_a_source(self):
        chunks = [{"text": "Quantum entanglement.", "metadata": {"source": "a.pdf", "page": 1}}]
        self.assertIsNone(match_citation_to_chunk(chunks, "Unrelated banana statement."))
        self.assertIsNone(match_citation_to_chunk(chunks, ""))


if __name__ == "__main__":
    unittest.main()
