"""
Motor RAG con ChromaDB y LangChain para la Plataforma Huella Forense.
Almacena vectorialmente la evidencia digital, informes periciales, cadenas de custodia y leyes procesales,
permitiendo búsquedas semánticas por similitud coseno/distancia L2 con filtros por rol y escenario.
"""

from __future__ import annotations
import os
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class RAGDocument(BaseModel):
    id: str
    case_id: str
    title: str
    category: str  # 'evidencia_forense', 'cadena_custodia', 'ley_procesal', 'informe_pericial'
    content: str
    allowed_roles: List[str]  # ['juez', 'fiscal', 'abogado_defensa', 'estudiante']
    metadata: Dict[str, Any] = {}

class ChromaRAGEngine:
    def __init__(self, persist_directory: Optional[str] = None):
        if persist_directory:
            os.makedirs(persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_directory)
        else:
            self.client = chromadb.EphemeralClient()
            
        self.collection = self.client.get_or_create_collection(
            name="huella_forense_knowledge",
            metadata={"description": "Evidencias y base pericial vectorial de Huella Forense"}
        )

    def index_document(self, doc: RAGDocument):
        """Indexa un documento de conocimiento con sus metadatos y control de acceso por rol."""
        roles_str = ",".join(doc.allowed_roles)
        meta = {
            "case_id": doc.case_id,
            "title": doc.title,
            "category": doc.category,
            "allowed_roles": roles_str
        }
        meta.update(doc.metadata)

        self.collection.upsert(
            ids=[doc.id],
            documents=[doc.content],
            metadatas=[meta]
        )

    def index_batch(self, docs: List[RAGDocument]):
        for d in docs:
            self.index_document(d)

    def query_context(self, case_id: str, query: str, requester_role: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Búsqueda semántica vectorial filtrada por caso_id y permisos de rol.
        Garantiza que la IA de cada personaje solo acceda a los autos procesales que le corresponden.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k * 2,  # Margen para filtrado por rol
            where={"case_id": case_id}
        )

        matched_docs = []
        if not results or not results["documents"] or not results["documents"][0]:
            return matched_docs

        docs = results["documents"][0]
        metadatas = results["metadatas"][0] if results["metadatas"] else []
        ids = results["ids"][0] if results["ids"] else []
        distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0]*len(docs)

        for i, text in enumerate(docs):
            meta = metadatas[i] if i < len(metadatas) else {}
            allowed = meta.get("allowed_roles", "").split(",")
            # Si el rol es el estudiante o el rol está explícitamente autorizado o es público
            if requester_role in allowed or "todos" in allowed or "publico" in allowed:
                matched_docs.append({
                    "id": ids[i],
                    "title": meta.get("title", "Documento Forense"),
                    "category": meta.get("category", "General"),
                    "content": text,
                    "distance": distances[i] if i < len(distances) else 0.0
                })

        return matched_docs[:top_k]

    def reset(self):
        self.client.delete_collection("huella_forense_knowledge")
        self.collection = self.client.get_or_create_collection(name="huella_forense_knowledge")
