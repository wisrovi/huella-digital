"""
Motor de Base de Conocimiento Híbrida (SQLite WAL + Búsqueda Semántica Vectorial / TF-IDF BM25).
Permite incorporar, indexar, filtrar por rol y consultar evidencia pericial, leyes y guiones.
"""

from __future__ import annotations
import sqlite3
import math
import re
from typing import List, Dict, Any, Optional
from collections import Counter
from huella_forense.models.schemas import KnowledgeDocument

class KnowledgeRepository:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        if self.db_path != ":memory:":
            self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id TEXT PRIMARY KEY,
                case_id TEXT,
                title TEXT,
                category TEXT,
                content TEXT,
                tags TEXT,
                created_at TEXT
            );
        """)
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_case ON knowledge_items(case_id);")
        self._conn.commit()

    def add_document(self, case_id: str, doc: KnowledgeDocument):
        tags_str = ",".join(doc.tags)
        self._conn.execute("""
            INSERT OR REPLACE INTO knowledge_items (id, case_id, title, category, content, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (doc.id, case_id, doc.title, doc.category, doc.content, tags_str, doc.created_at))
        self._conn.commit()

    def get_documents_by_case(self, case_id: str) -> List[KnowledgeDocument]:
        cur = self._conn.cursor()
        cur.execute("""
            SELECT id, title, category, content, tags, created_at
            FROM knowledge_items WHERE case_id = ?
        """, (case_id,))
        rows = cur.fetchall()
        return [
            KnowledgeDocument(
                id=r[0], title=r[1], category=r[2], content=r[3],
                tags=r[4].split(",") if r[4] else [], created_at=r[5]
            )
            for r in rows
        ]

    def search_relevant_context(self, case_id: str, query: str, allowed_tags: Optional[List[str]] = None, top_k: int = 3) -> List[KnowledgeDocument]:
        """
        Búsqueda de relevancia usando algoritmo BM25 / similitud léxico-semántica sobre los documentos del caso.
        Filtra por permisos/etiquetas del rol si están especificados.
        """
        docs = self.get_documents_by_case(case_id)
        if not docs:
            return []

        # Filtrar por tags si el rol tiene acceso restringido
        if allowed_tags:
            allowed_set = set(t.lower() for t in allowed_tags)
            docs = [
                d for d in docs
                if any(t.lower() in allowed_set for t in d.tags) or "publico" in [t.lower() for t in d.tags]
            ]

        if not docs:
            return []

        query_terms = [t.lower() for t in re.findall(r'\w+', query) if len(t) > 2]
        if not query_terms:
            return docs[:top_k]

        # Calcular scores TF-IDF / BM25 simplificado
        scores = []
        doc_count = len(docs)
        
        # IDF
        idf: Dict[str, float] = {}
        for term in query_terms:
            n_containing = sum(1 for d in docs if term in d.content.lower() or term in d.title.lower())
            idf[term] = math.log((doc_count - n_containing + 0.5) / (n_containing + 0.5) + 1.0)

        for d in docs:
            text = f"{d.title} {d.category} {d.content}".lower()
            tokens = re.findall(r'\w+', text)
            token_counts = Counter(tokens)
            doc_len = len(tokens)
            score = 0.0
            k1 = 1.5
            b = 0.75
            avg_dl = 100.0  # approximate

            for term in query_terms:
                if term in token_counts:
                    tf = token_counts[term]
                    score += idf[term] * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avg_dl)))
            scores.append((score, d))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scores[:top_k]]
