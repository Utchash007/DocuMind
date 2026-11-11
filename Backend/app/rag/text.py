"""Sentence splitting, sparse scoring, and evidence matching for v2 RAG."""

import math
import re
from collections import Counter


def split_into_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


class BM25Retriever:
    def __init__(self, corpus: list[dict]):
        self.corpus = corpus
        self.corpus_size = len(corpus)
        self.avg_doc_len = sum(len(c["text"].split()) for c in corpus) / self.corpus_size if self.corpus_size > 0 else 1
        self.doc_freqs = []
        self.idf = {}
        self.doc_lens = []
        words_in_docs = []
        for chunk in corpus:
            words = chunk["text"].lower().split()
            self.doc_lens.append(len(words))
            self.doc_freqs.append(Counter(words))
            words_in_docs.append(set(words))
        all_words = set(w for doc in words_in_docs for w in doc)
        for word in all_words:
            doc_count = sum(1 for doc_words in words_in_docs if word in doc_words)
            self.idf[word] = math.log((self.corpus_size - doc_count + 0.5) / (doc_count + 0.5) + 1.0)

    def get_scores(self, query: str, k1=1.5, b=0.75) -> dict:
        query_words = query.lower().split()
        scores = {}
        for i, chunk in enumerate(self.corpus):
            score = 0.0
            doc_len = self.doc_lens[i]
            doc_freq = self.doc_freqs[i]
            for word in query_words:
                if word in doc_freq:
                    tf = doc_freq[word]
                    idf = self.idf.get(word, 0.0)
                    denom = tf + k1 * (1 - b + b * doc_len / self.avg_doc_len)
                    score += idf * tf * (k1 + 1) / denom
            scores[chunk["id"]] = score
        return scores


def match_citation_to_chunk(
    chunks: list[dict], sentence: str, filename: str | None = None, page: int | None = None
) -> tuple[dict, str] | None:
    query_tokens = re.findall(r"\w+", sentence.lower())
    query_words = set(query_tokens)
    if not query_words:
        return None
    best_match = None
    best_score = (False, 0.0, 0.0, False, False)
    for chunk in chunks:
        metadata = chunk["metadata"]
        for candidate in split_into_sentences(chunk["text"]):
            candidate_tokens = re.findall(r"\w+", candidate.lower())
            words = set(candidate_tokens)
            common_words = len(query_words.intersection(words))
            overlap = common_words / len(query_words)
            precision = common_words / len(words) if words else 0.0
            score = (query_tokens == candidate_tokens, overlap, precision, metadata["source"] == filename, metadata["page"] == page)
            if overlap > 0 and score > best_score:
                best_match = (chunk, candidate)
                best_score = score
    return best_match
