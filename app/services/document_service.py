# re permite reconocer encabezados Markdown y conservar el nombre de cada sección.
import re
from dataclasses import dataclass
from pathlib import Path

from app.config import CHUNK_OVERLAP, CHUNK_SIZE

# El servicio está dos niveles debajo de la raíz de la aplicación del proyecto.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS_DIR = PROJECT_ROOT / "documents"


@dataclass
class DocumentChunk:
    """Fragmento de texto listo para generar un embedding y guardarse en Qdrant."""
    chunk_id: str
    text: str
    document: str
    section: str
    title: str | None = None
    page: int | None = None


def read_document(document_name: str) -> str:
    """Lee un documento validando que permanezca dentro de ``documents/``."""
    path = (DOCUMENTS_DIR / document_name).resolve()
    # La validación evita que un nombre malicioso lea archivos fuera del proyecto.
    if DOCUMENTS_DIR.resolve() not in path.parents:
        raise ValueError("El documento solicitado está fuera del directorio permitido")
    if not path.is_file():
        raise FileNotFoundError(f"No existe el documento {document_name}")
    return path.read_text(encoding="utf-8")


def split_into_sections(markdown: str) -> list[tuple[str, str]]:
    """Separa el Markdown en pares ``(sección, contenido)``."""
    sections: list[tuple[str, str]] = []
    current_section = "Introducción"
    current_lines: list[str] = []
    # Cada encabezado inicia una nueva sección; el texto anterior se conserva.
    for line in markdown.splitlines():
        heading = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if heading:
            content = "\n".join(current_lines).strip()
            if content:
                sections.append((current_section, content))
            current_section = heading.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)
    content = "\n".join(current_lines).strip()
    if content:
        sections.append((current_section, content))
    return sections


def _windows(text: str) -> list[str]:
    """Divide texto largo en ventanas con solapamiento para conservar contexto."""
    normalized = re.sub(r"\n{3,}", "\n\n", text.strip())
    if len(normalized) <= CHUNK_SIZE:
        return [normalized]
    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + CHUNK_SIZE, len(normalized))
        if end < len(normalized):
            # Preferimos cortar entre párrafos antes que partir una idea a la mitad.
            boundary = normalized.rfind("\n\n", start, end)
            if boundary > start + CHUNK_SIZE // 2:
                end = boundary
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        # El solapamiento reduce la pérdida de información en los límites.
        next_start = max(end - CHUNK_OVERLAP, start + 1)
        start = next_start
    return chunks


def chunk_document(document_name: str, markdown: str) -> list[DocumentChunk]:
    """Convierte un documento completo en chunks con IDs determinísticos."""
    chunks: list[DocumentChunk] = []
    for section, content in split_into_sections(markdown):
        # El índice global hace que cada chunk del documento tenga un ID único.
        for index, chunk_text in enumerate(_windows(content)):
            chunk_id = f"{Path(document_name).stem}-{len(chunks):04d}"
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                text=chunk_text,
                document=document_name,
                section=section,
                title=section,
            ))
    return chunks
