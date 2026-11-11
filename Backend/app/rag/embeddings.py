"""Batch embeddings: Hugging Face or Jina AI, mock only on demand.

* provider selected by ``DOCUMIND_EMBEDDING_PROVIDER`` (default ``hf``):
  Hugging Face ``sentence-transformers/all-MiniLM-L6-v2`` (384-d) or
  Jina AI ``jina-embeddings-v5-text-small`` (1024-d);
* both run in batches of 16 (``EMBEDDING_BATCH_SIZE``); responses are
  shape/finiteness validated before they can reach the index;
* Jina uses asymmetric retrieval adapters: ``retrieval.passage`` for
  indexed chunks (the default) and ``retrieval.query`` for questions;
* provider timeout defaults to 30 seconds (bounded).

**Mock-embedding guard (JOB-12).** Silent pseudo-random fallback is
prohibited in production: a document indexed
with random vectors would be marked ``Completed`` without semantic
retrieval.  Here, any provider failure raises
:class:`EmbeddingProviderError` and the job goes to ``retry_wait`` /
``failed``.  The deterministic fallback
(:func:`deterministic_fallback_embedding`) is used *only* when the service
is explicitly constructed with ``allow_mock=True`` -- tests and local
development opt in via ``DOCUMIND_ALLOW_MOCK_EMBEDDINGS=1``.  The
worker refuses to run in mock mode unless that variable is set, and
logs a loud warning when it is.
"""

from __future__ import annotations

import hashlib
import math
import os
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import httpx

EMBEDDING_PROVIDER_ENV_VAR = "DOCUMIND_EMBEDDING_PROVIDER"
PROVIDER_HF = "hf"
PROVIDER_JINA = "jina"
EMBEDDING_PROVIDERS = (PROVIDER_HF, PROVIDER_JINA)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
JINA_EMBEDDING_MODEL = "jina-embeddings-v5-text-small"
JINA_EMBEDDING_DIM = 1024
JINA_API_URL = "https://api.jina.ai/v1/embeddings"
TASK_RETRIEVAL_QUERY = "retrieval.query"
TASK_RETRIEVAL_PASSAGE = "retrieval.passage"
EMBEDDING_BATCH_SIZE = 16
DEFAULT_EMBEDDING_TIMEOUT_SECONDS = 30.0
# HF retired api-inference.huggingface.co (DNS no longer resolves); the
# Inference Providers router is the current documented endpoint.
HF_API_BASE = "https://router.huggingface.co/hf-inference/models"

MOCK_ENV_VAR = "DOCUMIND_ALLOW_MOCK_EMBEDDINGS"


class EmbeddingProviderError(Exception):
    """Embedding provider failed (retryable job error).

    Raised for network/timeout errors, non-200 responses, and
    malformed/short/wrong-dimension payloads.  Never silently replaced
    with mock vectors in production mode.
    """

    code = "embedding_provider_unavailable"
    retryable = True

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def deterministic_fallback_embedding(text: str, *, dim: int = EMBEDDING_DIM) -> list[float]:
    """Deterministic pseudo-random unit vector for a text (mock mode only).

    MD5-seeded PRNG,
    normalized to unit length.  Test/development use only -- production
    must never publish this as the index vector.  The ``dim`` keyword
    exists so test doubles can use smaller vectors; production callers
    must not pass it.
    """
    seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)
    rng = random.Random(seed)
    vector = [rng.uniform(-1.0, 1.0) for _ in range(dim)]
    magnitude = math.sqrt(sum(x * x for x in vector))
    if magnitude > 0:
        vector = [x / magnitude for x in vector]
    return vector


def mock_embeddings_allowed_from_env(env: dict[str, str] | None = None) -> bool:
    """True iff ``DOCUMIND_ALLOW_MOCK_EMBEDDINGS`` is explicitly enabled."""
    value = (env if env is not None else os.environ).get(MOCK_ENV_VAR, "")
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class EmbeddingConfig:
    """Embedding provider configuration (worker builds from env)."""

    provider: str = PROVIDER_HF
    model_id: str = EMBEDDING_MODEL
    timeout_seconds: float = DEFAULT_EMBEDDING_TIMEOUT_SECONDS
    batch_size: int = EMBEDDING_BATCH_SIZE
    dim: int = EMBEDDING_DIM
    allow_mock: bool = False
    api_url: str | None = None  # override for tests / mirrors

    def __post_init__(self) -> None:
        if self.provider not in EMBEDDING_PROVIDERS:
            raise ValueError(
                f"embedding provider must be one of {EMBEDDING_PROVIDERS!r}, "
                f"got {self.provider!r}"
            )

    @property
    def request_url(self) -> str:
        if self.provider == PROVIDER_JINA:
            return self.api_url or JINA_API_URL
        return self.api_url or f"{HF_API_BASE}/{self.model_id}/pipeline/feature-extraction"

    @classmethod
    def from_env(
        cls,
        env: dict[str, str] | None = None,
        *,
        allow_mock: bool | None = None,
    ) -> "EmbeddingConfig":
        """Build from environment; mock mode only via explicit opt-in.

        ``DOCUMIND_EMBEDDING_PROVIDER`` selects ``hf`` (default) or
        ``jina``.  Jina reads ``JINA_EMBEDDING_MODEL`` (default
        ``jina-embeddings-v5-text-small``) and always uses 1024-d
        vectors.  ``allow_mock=None`` reads
        ``DOCUMIND_ALLOW_MOCK_EMBEDDINGS``; an explicit boolean wins.
        """
        source = env if env is not None else os.environ
        mock = mock_embeddings_allowed_from_env(source) if allow_mock is None else allow_mock
        provider = (source.get(EMBEDDING_PROVIDER_ENV_VAR) or PROVIDER_HF).strip().lower()
        if provider not in EMBEDDING_PROVIDERS:
            raise ValueError(
                f"{EMBEDDING_PROVIDER_ENV_VAR} must be one of "
                f"{EMBEDDING_PROVIDERS!r}, got {provider!r}"
            )
        if provider == PROVIDER_JINA:
            model_id = (source.get("JINA_EMBEDDING_MODEL") or JINA_EMBEDDING_MODEL).strip()
            return cls(
                provider=PROVIDER_JINA,
                model_id=model_id,
                dim=JINA_EMBEDDING_DIM,
                allow_mock=mock,
            )
        return cls(allow_mock=mock)


# Callable with the same shape as httpx.post for tests:
# (url, *, headers, json, timeout) -> response with .status_code/.json()
HttpPost = Callable[..., "httpx.Response"]


class EmbeddingService:
    """Protocol-shaped embedding provider (``PdfPipeline.embed_texts``).

    ``http_post`` is injectable so tests can use ``httpx.MockTransport``
    or a recording stub without network access.  In mock mode the
    provider is never called at all.
    """

    def __init__(
        self,
        config: EmbeddingConfig | None = None,
        *,
        api_key: str | None = None,
        http_post: HttpPost | None = None,
    ) -> None:
        self.config = config or EmbeddingConfig()
        if api_key is not None:
            self._api_key = api_key or None
        elif self.config.provider == PROVIDER_JINA:
            self._api_key = os.environ.get("JINA_API_KEY") or None
        else:
            self._api_key = (
                os.environ.get("HF_API_KEY") or os.environ.get("HF_TOKEN") or None
            )
        self._http_post: HttpPost = http_post or httpx.post

    @property
    def allow_mock(self) -> bool:
        return self.config.allow_mock

    def embed_texts(
        self,
        texts: Sequence[str],
        *,
        task: str | None = None,
    ) -> list[list[float]]:
        """Embed ``texts`` in batches of ``config.batch_size``.

        Returns one vector per input, in order.  Raises
        :class:`EmbeddingProviderError` on any provider failure (unless
        mock mode is enabled, in which case the provider is not called).

        ``task`` is a Jina retrieval adapter hint: ``retrieval.passage``
        (the default) for indexed chunks, ``retrieval.query`` for
        questions.  Hugging Face ignores it.
        """
        items = list(texts)
        if not items:
            return []
        if self.config.allow_mock:
            return [
                deterministic_fallback_embedding(text, dim=self.config.dim) for text in items
            ]
        embeddings: list[list[float]] = []
        batch_size = max(1, self.config.batch_size)
        for start in range(0, len(items), batch_size):
            embeddings.extend(
                self._embed_batch(items[start : start + batch_size], task=task)
            )
        return embeddings

    def _embed_batch(
        self, batch: list[str], *, task: str | None = None
    ) -> list[list[float]]:
        if self.config.provider == PROVIDER_JINA:
            return self._embed_jina_batch(batch, task=task)
        return self._embed_hf_batch(batch)

    def _embed_hf_batch(self, batch: list[str]) -> list[list[float]]:
        payload = self._post({"inputs": batch, "options": {"wait_for_model": True}})
        return self._validate(payload, expected=len(batch))

    def _embed_jina_batch(
        self, batch: list[str], *, task: str | None = None
    ) -> list[list[float]]:
        if not self._api_key:
            raise EmbeddingProviderError(
                "JINA_API_KEY is not configured for the jina embedding provider"
            )
        payload = self._post(
            {
                "model": self.config.model_id,
                "input": batch,
                "task": task or TASK_RETRIEVAL_PASSAGE,
                "dimensions": self.config.dim,
                "normalized": True,
            }
        )
        return self._validate_jina(payload, expected=len(batch))

    def _post(self, payload: dict[str, object]) -> object:
        headers: dict[str, str] = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        try:
            response = self._http_post(
                self.config.request_url,
                headers=headers,
                json=payload,
                timeout=self.config.timeout_seconds,
            )
        except Exception as exc:
            raise EmbeddingProviderError(f"embedding provider request failed: {exc}") from exc
        if response.status_code != 200:
            detail = str(getattr(response, "text", "") or "").strip()
            suffix = f": {detail[:300]}" if detail else ""
            raise EmbeddingProviderError(
                f"embedding provider returned HTTP {response.status_code}{suffix}"
            )
        try:
            return response.json()
        except Exception as exc:
            raise EmbeddingProviderError(f"embedding provider returned invalid JSON: {exc}") from exc

    def _validate_jina(self, payload: object, *, expected: int) -> list[list[float]]:
        """Validate Jina's OpenAI-shaped ``{"data": [{"index", "embedding"}]}``."""
        if not isinstance(payload, dict):
            raise EmbeddingProviderError(
                f"embedding provider returned {type(payload).__name__}, expected an object"
            )
        data = payload.get("data")
        if not isinstance(data, list) or len(data) != expected:
            count = len(data) if isinstance(data, list) else "n/a"
            raise EmbeddingProviderError(
                f"embedding provider returned {count} vectors, expected {expected}"
            )
        ordered: list[object] = [None] * expected
        for position, item in enumerate(data):
            if not isinstance(item, dict):
                raise EmbeddingProviderError(
                    "embedding provider returned a non-object data item"
                )
            index = item.get("index", position)
            if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < expected:
                raise EmbeddingProviderError(
                    f"embedding provider returned an invalid vector index {index!r}"
                )
            if ordered[index] is not None:
                raise EmbeddingProviderError(
                    f"embedding provider returned duplicate vector index {index}"
                )
            ordered[index] = item.get("embedding")
        if any(vector is None for vector in ordered):
            raise EmbeddingProviderError(
                "embedding provider returned fewer vectors than requested"
            )
        return self._validate(ordered, expected=expected)

    def _validate(self, payload: object, *, expected: int) -> list[list[float]]:
        dim = self.config.dim
        if not isinstance(payload, list) or len(payload) != expected:
            raise EmbeddingProviderError(
                f"embedding provider returned {type(payload).__name__} "
                f"of length {len(payload) if isinstance(payload, list) else 'n/a'}, "
                f"expected {expected}"
            )
        vectors: list[list[float]] = []
        for vector in payload:
            if not isinstance(vector, (list, tuple)) or len(vector) != dim:
                raise EmbeddingProviderError(
                    f"embedding vector must have {dim} dimensions"
                )
            try:
                values = [float(component) for component in vector]
            except (TypeError, ValueError) as exc:
                raise EmbeddingProviderError("embedding vector has non-numeric values") from exc
            if not all(math.isfinite(value) for value in values):
                raise EmbeddingProviderError("embedding vector has non-finite values")
            vectors.append(values)
        return vectors


__all__ = [
    "EMBEDDING_BATCH_SIZE",
    "EMBEDDING_DIM",
    "EMBEDDING_MODEL",
    "EMBEDDING_PROVIDERS",
    "EMBEDDING_PROVIDER_ENV_VAR",
    "HF_API_BASE",
    "JINA_API_URL",
    "JINA_EMBEDDING_DIM",
    "JINA_EMBEDDING_MODEL",
    "MOCK_ENV_VAR",
    "PROVIDER_HF",
    "PROVIDER_JINA",
    "TASK_RETRIEVAL_PASSAGE",
    "TASK_RETRIEVAL_QUERY",
    "EmbeddingConfig",
    "EmbeddingProviderError",
    "EmbeddingService",
    "deterministic_fallback_embedding",
    "mock_embeddings_allowed_from_env",
]
