import re

from pydantic import BaseModel, Field

from app.rag.loader import Document


class Chunk(BaseModel):
    chunk_id: str
    page_content: str
    metadata: dict = Field(default_factory=dict)


class SentenceAwareChunker:
    def __init__(
        self,
        min_target_size: int = 500,
        max_target_size: int = 800,
        min_overlap: int = 50,
        max_overlap: int = 100,
    ):
        self.min_target_size = min_target_size
        self.max_target_size = max_target_size
        self.min_overlap = min_overlap
        self.max_overlap = max_overlap

    def chunk_document(self, doc: Document) -> list[Chunk]:
        paragraphs = doc.page_content.split("\n\n")
        chunks: list[Chunk] = []
        current_sentences: list[str] = []
        chunk_count = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            sentences = self._split_into_sentences(paragraph)
            for sentence in sentences:
                test_sentences = current_sentences + [sentence]
                test_text = " ".join(test_sentences)

                # If adding this sentence exceeds the max size,
                # flush the current chunk first.
                if len(test_text) > self.max_target_size and current_sentences:
                    chunk_count += 1
                    chunk_text = " ".join(current_sentences)
                    chunks.append(self._create_chunk(chunk_text, doc, chunk_count))

                    # Start next chunk with overlap
                    overlap_sentences = self._build_overlap_sentences(current_sentences)
                    current_sentences = overlap_sentences + [sentence]
                else:
                    current_sentences.append(sentence)

        # Flush remaining text
        if current_sentences:
            chunk_count += 1
            chunk_text = " ".join(current_sentences)
            chunks.append(self._create_chunk(chunk_text, doc, chunk_count))

        return chunks

    def _split_into_sentences(self, text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _build_overlap_sentences(self, sentences: list[str]) -> list[str]:
        overlap: list[str] = []
        total = 0
        for sentence in reversed(sentences):
            length = len(sentence)
            if total + length > self.max_overlap:
                break

            overlap.insert(0, sentence)
            total += length

            if total >= self.min_overlap:
                break

        return overlap

    def _create_chunk(self, text: str, doc: Document, index: int) -> Chunk:
        metadata = doc.metadata.copy()
        metadata.update(
            {
                "document_id": doc.id,
                "chunk_index": index,
                "character_count": len(text),
            }
        )

        return Chunk(
            chunk_id=f"{doc.id}_chunk_{index}",
            page_content=text,
            metadata=metadata,
        )
