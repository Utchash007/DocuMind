# `app/rag/__init__.py`

[Source](../../../../Backend/app/rag/__init__.py) · [Backend index](../../README.md)

Re-exports the PDF/indexing portion of the RAG package through `__all__`:

- [pdf.md](pdf.md): extraction facade/function, PDF error classes, target chunk length, sentence splitting.
- [embeddings.md](embeddings.md): default HF dimension, embedding service/error, deterministic mock-vector helper.
- [indexing.md](indexing.md): collection name/metadata keys, index service/error, metadata and chunk-ID builders.

No functions or classes are defined locally. Imports load declarations; provider requests happen when services are called. Retrieval, generation, citation refinement, and provider-specific configuration are imported from their explicit modules, not exported here. The `chunk_id_for` export is the indexing wrapper around the PDF implementation.
