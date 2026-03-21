import re
from typing import List


def split_text_by_paragraphs(text: str) -> List[str]:
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
    return paragraphs


def split_text_by_sentences(text: str, max_length: int = 1000) -> List[str]:
    sentences = re.split(r'(?<=[。！？.!?])\s*', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def split_text(text: str, max_chunk_length: int = 2000) -> List[str]:
    paragraphs = split_text_by_paragraphs(text)

    if len(paragraphs) > 1:
        return paragraphs

    if len(text) <= max_chunk_length:
        return [text]

    return split_text_by_sentences(text, max_chunk_length)


def merge_results(results: List[str], original_chunks: List[str]) -> str:
    if len(original_chunks) == 1:
        return results[0]

    separator = "\n\n" if "\n\n" in "\n\n".join(original_chunks) else "\n"
    return separator.join(results)
