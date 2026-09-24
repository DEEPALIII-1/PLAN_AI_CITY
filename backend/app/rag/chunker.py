import re
from typing import List, Dict, Any

class DocumentChunker:
    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Splits text into chunks respecting paragraphs and sentence boundaries.
        """
        if not text:
            return []
        
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        current_chunk = ""
        current_words = 0
        chunk_index = 0

        for p in paragraphs:
            words = p.split()
            if current_words + len(words) <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + p
                else:
                    current_chunk = p
                current_words += len(words)
            else:
                # If current chunk has content, save it
                if current_chunk:
                    chunks.append({
                        "chunk_index": chunk_index,
                        "content": current_chunk,
                        "metadata": metadata or {}
                    })
                    chunk_index += 1
                    # Handle overlap by taking the last N words
                    overlap_words = current_chunk.split()[-self.chunk_overlap:]
                    current_chunk = " ".join(overlap_words) + "\n\n" + p
                    current_words = len(overlap_words) + len(words)
                else:
                    # Single paragraph exceeds chunk_size, split by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', p)
                    for s in sentences:
                        s_words = s.split()
                        if current_words + len(s_words) <= self.chunk_size:
                            current_chunk = (current_chunk + " " + s).strip()
                            current_words += len(s_words)
                        else:
                            if current_chunk:
                                chunks.append({
                                    "chunk_index": chunk_index,
                                    "content": current_chunk,
                                    "metadata": metadata or {}
                                })
                                chunk_index += 1
                            current_chunk = s
                            current_words = len(s_words)

        if current_chunk.strip():
            chunks.append({
                "chunk_index": chunk_index,
                "content": current_chunk.strip(),
                "metadata": metadata or {}
            })

        return chunks

chunker = DocumentChunker()
