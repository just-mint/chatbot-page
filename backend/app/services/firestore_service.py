from datetime import datetime, timezone
from firebase_admin import firestore
from backend.app.core.firebase_config import get_firestore

_db = None

def _get_db():
    global _db
    if _db is None:
        _db = get_firestore()
    return _db


def _notes_col(uid: str):
    return _get_db().collection("notes").document(uid).collection("items")


def save_note(uid: str, title: str, content: str) -> str:
    doc = {
        "title": title,
        "content": content,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    _, ref = _notes_col(uid).add(doc)
    return ref.id

def load_notes(uid: str, limit: int = 100) -> list[dict]:
    docs = list(
        _notes_col(uid)
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    result = []
    for d in docs:
        data = d.to_dict()
        result.append({
            "id": d.id,
            "title": data.get("title", ""),
            "content": data.get("content", ""),
            "created_at": data.get("created_at").isoformat() if data.get("created_at") else None,
            "updated_at": data.get("updated_at").isoformat() if data.get("updated_at") else None,
        })
    return result


def update_note(uid: str, note_id: str, title: str | None, content: str | None):
    updates = {"updated_at": datetime.now(timezone.utc)}
    if title is not None:
        updates["title"] = title
    if content is not None:
        updates["content"] = content
    _notes_col(uid).document(note_id).update(updates)


def delete_note(uid: str, note_id: str):
    _notes_col(uid).document(note_id).delete()