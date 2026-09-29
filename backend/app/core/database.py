import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.core.config import settings


def get_db_connection():
    conn = sqlite3.connect(settings.TELEMETRY_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize SQLite database for feedback, audits, and query telemetry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Queries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS queries (
        id TEXT PRIMARY KEY,
        query_text TEXT,
        response_text TEXT,
        mode TEXT,
        standard_filtered TEXT,
        confidence_score REAL,
        citations_json TEXT,
        is_hallucination_safe INTEGER,
        refusal_triggered INTEGER,
        created_at TEXT
    )
    """)
    
    # Feedback table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id TEXT PRIMARY KEY,
        query_id TEXT,
        rating TEXT,
        query_text TEXT,
        response_text TEXT,
        mode TEXT,
        comments TEXT,
        created_at TEXT,
        FOREIGN KEY (query_id) REFERENCES queries (id)
    )
    """)
    
    # Audits table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audits (
        id TEXT PRIMARY KEY,
        standard_is_code TEXT,
        standard_title TEXT,
        product_name TEXT,
        manufacturer_name TEXT,
        batch_number TEXT,
        testing_lab TEXT,
        overall_verdict TEXT,
        passed_count INTEGER,
        failed_count INTEGER,
        warning_count INTEGER,
        total_count INTEGER,
        compliance_score REAL,
        summary TEXT,
        parameter_results_json TEXT,
        created_at TEXT
    )
    """)
    
    # Standards registry metadata table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS standards_registry (
        is_code TEXT PRIMARY KEY,
        title TEXT,
        year TEXT,
        category TEXT,
        chunk_count INTEGER,
        table_count INTEGER,
        created_at TEXT
    )
    """)
    
    conn.commit()
    conn.close()


def log_query(
    query_id: str,
    query_text: str,
    response_text: str,
    mode: str,
    standard_filtered: Optional[str],
    confidence_score: float,
    citations: List[Dict[str, Any]],
    is_hallucination_safe: bool,
    refusal_triggered: bool
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO queries 
    (id, query_text, response_text, mode, standard_filtered, confidence_score, citations_json, is_hallucination_safe, refusal_triggered, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        query_id,
        query_text,
        response_text,
        mode,
        standard_filtered,
        confidence_score,
        json.dumps(citations),
        1 if is_hallucination_safe else 0,
        1 if refusal_triggered else 0,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def log_feedback(
    feedback_id: str,
    query_id: str,
    rating: str,
    query_text: Optional[str],
    response_text: Optional[str],
    mode: Optional[str],
    comments: Optional[str]
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO feedback 
    (id, query_id, rating, query_text, response_text, mode, comments, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        feedback_id,
        query_id,
        rating,
        query_text,
        response_text,
        mode,
        comments,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def log_audit(
    audit_id: str,
    standard_is_code: str,
    standard_title: str,
    product_name: str,
    manufacturer_name: str,
    batch_number: str,
    testing_lab: str,
    overall_verdict: str,
    passed_count: int,
    failed_count: int,
    warning_count: int,
    total_count: int,
    compliance_score: float,
    summary: str,
    parameter_results: List[Dict[str, Any]]
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO audits
    (id, standard_is_code, standard_title, product_name, manufacturer_name, batch_number, testing_lab, 
     overall_verdict, passed_count, failed_count, warning_count, total_count, compliance_score, summary, parameter_results_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        audit_id,
        standard_is_code,
        standard_title,
        product_name,
        manufacturer_name,
        batch_number,
        testing_lab,
        overall_verdict,
        passed_count,
        failed_count,
        warning_count,
        total_count,
        compliance_score,
        summary,
        json.dumps(parameter_results),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def register_standard_db(
    is_code: str,
    title: str,
    year: str,
    category: str,
    chunk_count: int,
    table_count: int
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO standards_registry
    (is_code, title, year, category, chunk_count, table_count, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        is_code,
        title,
        year,
        category,
        chunk_count,
        table_count,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def get_all_standards_db() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM standards_registry ORDER BY is_code ASC")
    rows = cursor.fetchall()
    standards = [dict(row) for row in rows]
    conn.close()
    return standards


def get_standard_by_code_db(is_code: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM standards_registry WHERE is_code = ?", (is_code,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_standard_db(is_code: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM standards_registry WHERE is_code = ?", (is_code,))
    conn.commit()
    conn.close()
