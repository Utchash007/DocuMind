import re
from contextlib import ExitStack, contextmanager
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

from app import main
from app.utils import get_fallback_embedding, split_into_sentences


def make_pdf(pages: list[str]) -> bytes:
    writer = PdfWriter()
    font = writer._add_object(DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    }))
    for text in pages:
        page = writer.add_blank_page(width=612, height=792)
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font}),
        })
        stream = DecodedStreamObject()
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream.set_data(f"BT /F1 12 Tf 50 740 Td ({escaped}) Tj ET".encode("latin-1"))
        page[NameObject("/Contents")] = writer._add_object(stream)
    result = BytesIO()
    writer.write(result)
    return result.getvalue()


class MemoryCollection:
    def __init__(self):
        self.chunks = {}
        self.filters = []

    def get(self, where=None, include=None):
        self.filters.append(where)
        source = where.get("source") if where else None
        sources = source.get("$in") if isinstance(source, dict) else ([source] if source else None)
        chunks = [chunk for chunk in self.chunks.values() if sources is None or chunk["metadata"]["source"] in sources]
        return {
            "ids": [chunk["id"] for chunk in chunks],
            "documents": [chunk["text"] for chunk in chunks],
            "metadatas": [chunk["metadata"] for chunk in chunks],
        }

    def upsert(self, ids, embeddings, documents, metadatas):
        for index, identifier in enumerate(ids):
            self.chunks[identifier] = {
                "id": identifier, "text": documents[index], "metadata": metadatas[index],
            }

    def add(self, **kwargs):
        self.upsert(**kwargs)

    def delete(self, where=None, ids=None):
        for identifier in ids if ids is not None else self.get(where)["ids"]:
            self.chunks.pop(identifier, None)

    def query(self, query_embeddings, n_results, where=None):
        data = self.get(where)
        ids = data["ids"][:n_results]
        return {"ids": [ids], "distances": [[0.1] * len(ids)]}


def answer_from_context(**kwargs):
    context = kwargs["messages"][-1]["content"]
    passages = re.findall(
        r"\[Document Chunk \d+ \| Source: (.*?) \| Page (\d+)\]: (.*?)(?=\n\n\[Document Chunk|\n\nQuestion:)",
        context,
        flags=re.DOTALL,
    )
    citations = [main.Citation(sentence=split_into_sentences(text)[0], page=int(page), filename=filename)
                 for filename, page, text in passages]
    return main.AnswerResponse(
        answer="## Source overview\n\n" + "\n\n".join(citation.sentence for citation in citations),
        citations=citations,
    )


@contextmanager
def isolated_backend(directory: Path):
    collection = MemoryCollection()
    completions = SimpleNamespace(create=answer_from_context)
    instructor_client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    with ExitStack() as stack:
        stack.enter_context(patch.object(main, "UPLOAD_DIR", directory))
        stack.enter_context(patch.object(main, "get_chroma_collection", return_value=collection))
        stack.enter_context(patch.object(main, "get_embeddings_batch", side_effect=lambda texts: [get_fallback_embedding(text) for text in texts]))
        stack.enter_context(patch.object(main, "Groq", return_value=object()))
        stack.enter_context(patch.object(main.instructor, "from_groq", return_value=instructor_client))
        stack.enter_context(patch.dict("os.environ", {"GROQ_API_KEY": "notemind-test-key"}))
        yield collection, completions
