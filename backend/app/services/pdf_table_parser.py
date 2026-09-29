import re
import os
from typing import List, Dict, Any, Tuple, Optional
import pdfplumber
import pymupdf as fitz


class ParsedChunk:
    def __init__(
        self,
        text: str,
        is_code: str,
        doc_title: str,
        clause: str,
        page_number: int,
        is_table: bool = False,
        table_number: Optional[str] = None,
        table_title: Optional[str] = None,
        table_data: Optional[Dict[str, Any]] = None
    ):
        self.text = text
        self.is_code = is_code
        self.doc_title = doc_title
        self.clause = clause
        self.page_number = page_number
        self.is_table = is_table
        self.table_number = table_number
        self.table_title = table_title
        self.table_data = table_data or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "is_code": self.is_code,
            "doc_title": self.doc_title,
            "clause": self.clause,
            "page_number": self.page_number,
            "is_table": self.is_table,
            "table_number": self.table_number or "",
            "table_title": self.table_title or "",
            "table_data": self.table_data
        }


class TableAwarePDFParser:
    """
    Advanced PDF ingestion pipeline designed specifically for Bureau of Indian Standards (BIS).
    Preserves table structures (chemical limits, tolerances, physical metrics)
    by extracting tables into formatted Markdown and semantic key-value records,
    preventing row/column degradation during vector chunking.
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_is_code_and_title(self, text_sample: str) -> Tuple[str, str]:
        """Attempt to extract IS code and title from the first page text."""
        # Match patterns like 'IS 14543 : 2018' or 'IS:14543' or 'INDIAN STANDARD IS 1293'
        is_match = re.search(r'IS\s*[:\s]?\s*(\d{3,5}(?:\s*\([^)]+\))?(?:\s*:\s*\d{4})?)', text_sample, re.IGNORECASE)
        is_code = f"IS {is_match.group(1).strip()}" if is_match else "IS UNKNOWN"
        
        # Look for standard title heuristic
        lines = [line.strip() for line in text_sample.split("\n") if line.strip()]
        title = "Indian Standard Specification"
        for i, line in enumerate(lines[:15]):
            if "standard" in line.lower() or "specification" in line.lower() or "requirements" in line.lower():
                if len(line) > 10:
                    title = line
                    break
        return is_code, title

    def _clean_cell(self, cell: Any) -> str:
        if cell is None:
            return ""
        return str(cell).replace("\n", " ").strip()

    def _convert_table_to_markdown_and_records(
        self,
        table: List[List[Any]],
        table_number: str,
        table_title: str,
        is_code: str,
        clause: str
    ) -> Tuple[str, List[Dict[str, str]]]:
        """Convert a 2D table array into both Markdown representation and semantic row records."""
        if not table or len(table) < 2:
            return "", []

        # Header row
        headers = [self._clean_cell(c) or f"Col_{idx+1}" for idx, c in enumerate(table[0])]
        
        # Markdown table construction
        md_lines = []
        md_lines.append(f"### {table_number}: {table_title}")
        md_lines.append(f"**Standard:** {is_code} | **Clause:** {clause}")
        md_lines.append("")
        md_lines.append("| " + " | ".join(headers) + " |")
        md_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        semantic_records = []

        for row_idx, row in enumerate(table[1:]):
            cleaned_row = [self._clean_cell(c) for c in row]
            # Pad or trim to header length
            while len(cleaned_row) < len(headers):
                cleaned_row.append("")
            cleaned_row = cleaned_row[:len(headers)]
            
            # Skip empty rows
            if not any(cleaned_row):
                continue

            md_lines.append("| " + " | ".join(cleaned_row) + " |")

            # Create semantic contextual representation for vector retrieval
            row_dict = {}
            row_desc_parts = [f"In {is_code} ({table_number} - {table_title}, {clause}):"]
            for h, val in zip(headers, cleaned_row):
                if val:
                    row_dict[h] = val
                    row_desc_parts.append(f"{h}: {val}")
            
            semantic_records.append({
                "raw_dict": row_dict,
                "text_summary": " | ".join(row_desc_parts)
            })

        markdown_text = "\n".join(md_lines)
        return markdown_text, semantic_records

    def parse_pdf(
        self,
        pdf_path: str,
        manual_is_code: Optional[str] = None,
        manual_title: Optional[str] = None
    ) -> List[ParsedChunk]:
        """
        Extracts both structured tables and hierarchical text clauses from a BIS Standard PDF.
        """
        all_chunks: List[ParsedChunk] = []

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found at {pdf_path}")

        # First pass with PyMuPDF to extract general document text and metadata
        doc = fitz.open(pdf_path)
        first_page_text = doc[0].get_text() if len(doc) > 0 else ""
        
        detected_code, detected_title = self.extract_is_code_and_title(first_page_text)
        is_code = manual_is_code.strip() if manual_is_code else detected_code
        doc_title = manual_title.strip() if manual_title else detected_title

        # Open with pdfplumber for table extraction
        with pdfplumber.open(pdf_path) as pdf:
            current_clause = "Clause 1.0 Scope"
            
            for page_idx, page in enumerate(pdf.pages):
                page_num = page_idx + 1
                
                # 1. Extract tables
                tables = page.extract_tables()
                table_bboxes = []
                
                # Check for table title patterns in page text
                raw_page_text = page.extract_text() or ""
                
                for t_idx, table in enumerate(tables):
                    if not table or len(table) < 2:
                        continue
                    
                    # Detect Table Number and Title
                    t_num_match = re.search(r'(Table\s+\d+[A-Za-z]?)\s*[:\-\.]?\s*([^\n\.\(]+)', raw_page_text, re.IGNORECASE)
                    if t_num_match:
                        table_number = t_num_match.group(1).strip()
                        table_title = t_num_match.group(2).strip()
                    else:
                        table_number = f"Table {t_idx + 1}"
                        table_title = f"Requirements Specification (Page {page_num})"

                    # Check for clause near table
                    clause_match = re.search(r'(\b(?:Clause|Section|\d+\.\d+)\b[^\n\:]*)', raw_page_text)
                    if clause_match:
                        current_clause = clause_match.group(1).strip()

                    md_table, semantic_records = self._convert_table_to_markdown_and_records(
                        table, table_number, table_title, is_code, current_clause
                    )

                    if md_table:
                        # Add complete table markdown chunk
                        table_chunk_text = (
                            f"BIS STANDARD: {is_code} - {doc_title}\n"
                            f"PAGE: {page_num} | CLAUSE: {current_clause}\n\n"
                            f"{md_table}\n\n"
                            f"Detailed Specifications:\n" +
                            "\n".join([f"- {r['text_summary']}" for r in semantic_records])
                        )

                        headers = [self._clean_cell(c) for c in table[0]]
                        cleaned_rows = [[self._clean_cell(c) for c in row] for row in table[1:]]

                        all_chunks.append(
                            ParsedChunk(
                                text=table_chunk_text,
                                is_code=is_code,
                                doc_title=doc_title,
                                clause=current_clause,
                                page_number=page_num,
                                is_table=True,
                                table_number=table_number,
                                table_title=table_title,
                                table_data={
                                    "columns": headers,
                                    "rows": cleaned_rows,
                                    "markdown": md_table,
                                    "record_count": len(semantic_records)
                                }
                            )
                        )

                # 2. Extract Non-Table Text hierarchically
                paragraphs = raw_page_text.split("\n\n")
                for para in paragraphs:
                    para = para.strip()
                    if not para or len(para) < 25:
                        continue
                    
                    # Update clause if encountered
                    clause_heading = re.search(r'^(\d+(?:\.\d+)*\s+[A-Z][A-Za-z\s]{3,40})', para)
                    if clause_heading:
                        current_clause = clause_heading.group(1).strip()

                    # Chunk long text paragraphs
                    if len(para) > self.chunk_size:
                        sub_chunks = [para[i:i + self.chunk_size] for i in range(0, len(para), self.chunk_size - self.chunk_overlap)]
                        for sub in sub_chunks:
                            chunk_text = f"BIS STANDARD: {is_code} ({doc_title})\nPAGE: {page_num} | CLAUSE: {current_clause}\n\n{sub}"
                            all_chunks.append(
                                ParsedChunk(
                                    text=chunk_text,
                                    is_code=is_code,
                                    doc_title=doc_title,
                                    clause=current_clause,
                                    page_number=page_num,
                                    is_table=False
                                )
                            )
                    else:
                        chunk_text = f"BIS STANDARD: {is_code} ({doc_title})\nPAGE: {page_num} | CLAUSE: {current_clause}\n\n{para}"
                        all_chunks.append(
                            ParsedChunk(
                                text=chunk_text,
                                is_code=is_code,
                                doc_title=doc_title,
                                clause=current_clause,
                                page_number=page_num,
                                is_table=False
                            )
                        )

        return all_chunks
