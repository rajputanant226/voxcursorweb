import uuid
import os
from qdrant_client.models import PayloadSchemaType
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
)
from openai import OpenAI

# ---------- OPENAI ----------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- QDRANT ----------
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

COLLECTION = "voxcursor_memory"
VECTOR_SIZE = 1536


# ---------- SAFE COLLECTION CHECK ----------
def ensure_collection():
    collections = qdrant.get_collections().collections
    names = [c.name for c in collections]

    if COLLECTION not in names:
        qdrant.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

    # ---- CREATE PAYLOAD INDEXES (SAFE & IDEMPOTENT) ----
    qdrant.create_payload_index(
        collection_name=COLLECTION,
        field_name="user_id",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    qdrant.create_payload_index(
        collection_name=COLLECTION,
        field_name="type",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    qdrant.create_payload_index(
        collection_name=COLLECTION,
        field_name="key",
        field_schema=PayloadSchemaType.KEYWORD,
    )

# IMPORTANT: call once
ensure_collection()


# ---------- EMBEDDING ----------
def embed(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


# ---------- STORE USER NAME ----------
def store_user_name(user_id: str, name: str):
    qdrant.upsert(
        collection_name=COLLECTION,
        points=[
            {
                "id": str(uuid.uuid4()),
                "vector": embed(f"user name is {name}"),
                "payload": {
                    "user_id": user_id,
                    "type": "profile",
                    "key": "name",
                    "value": name,
                },
            }
        ],
    )


# ---------- GET USER NAME ----------
def get_user_name(user_id: str):
    records, _ = qdrant.scroll(
        collection_name=COLLECTION,
        scroll_filter=Filter(
            must=[
                FieldCondition(key="user_id", match=MatchValue(value=user_id)),
                FieldCondition(key="type", match=MatchValue(value="profile")),
                FieldCondition(key="key", match=MatchValue(value="name")),
            ]
        ),
        limit=1,
    )

    if records:
        return records[0].payload.get("value")

    return None
