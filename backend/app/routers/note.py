from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.dependencies.auth import get_current_user
from backend.app.schemas.note import NoteCreate, NoteUpdate
from backend.app.services.firestore_service import save_note, load_notes, update_note, delete_note

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("")
def get_notes(user=Depends(get_current_user)):
    notes = load_notes(user["uid"])
    return notes


@router.post("")
def create_note(payload: NoteCreate, user=Depends(get_current_user)):
    try:
        note_id = save_note(user["uid"], payload.title, payload.content)
        return {"id": note_id, "message": "Đã tạo ghi chú"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{note_id}")
def edit_note(note_id: str, payload: NoteUpdate, user=Depends(get_current_user)):
    try:
        update_note(user["uid"], note_id, payload.title, payload.content)
        return {"message": "Đã cập nhật ghi chú"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
 
@router.delete("/{note_id}")
def remove_note(note_id: str, user=Depends(get_current_user)):
    try:
        delete_note(user["uid"], note_id)
        return {"message": "Đã xóa ghi chú"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))