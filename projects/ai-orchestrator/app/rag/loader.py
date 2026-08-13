
from pydantic import BaseModel, Field
from typing import List
from app.logger.logger import logger
from pathlib import Path

class Document(BaseModel):
    id: str
    page_content: str
    metadata: dict = Field(default_factory=dict)


class KnowledgeLoader:

    def __init__(self, directory:str):
        self.directory_path = Path(directory)


    def load_document(self) -> List[Document]:
       """
        Reads all files in the configured directory and returns a list of Document objects.
        """
       documents = []

       if not self.directory_path.exists() or not self.directory_path.is_dir():
            logger.info(f"[Warning] directory '{self.directory_path}' not found.")
            return documents       

       for file_path in self.directory_path.glob("*.md"):
           try:
               # Read content safely with UTF-8 encoding
               content = file_path.read_text(encoding="utf-8")
               # Construct metadata payload for tracking source info
               metadata = {
                    "source": file_path.name,
                    "path": str(file_path),
                    "size_bytes": file_path.stat().st_size
                }
               documents.append(Document(id = file_path.name, page_content = content, metadata= metadata))
           except Exception as e:
               logger.info(f"[Error] Failed to read {file_path.name}: {str(e)}")

       return documents    
    
