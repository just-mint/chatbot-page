import requests

API_BASE = "http://localhost:8000"

# Authentication
def signup(email: str, password: str):
    r = requests.post(f"{API_BASE}/auth/signup", json={
        "email": email,
        "password": password
    })
    r.raise_for_status()
    return r.json()

def login(email: str, password: str):
    r = requests.post(f"{API_BASE}/auth/login", json={
        "email": email,
        "password": password
    })
    r.raise_for_status()
    return r.json()

def google_login(id_token: str):
    r = requests.post(f"{API_BASE}/auth/google", json={
        "id_token": id_token
    })
    r.raise_for_status()
    return r.json()

# Note
def get_notes(id_token: str):
    r = requests.get(
        f"{API_BASE}/notes",
        headers={"Authorization": f"Bearer {id_token}"}
    )
    r.raise_for_status()
    return r.json()

def create_note(id_token: str, title: str, content: str):
    r = requests.post(
        f"{API_BASE}/notes",
        json={"title": title, "content": content},
        headers={"Authorization": f"Bearer {id_token}"}
    )
    r.raise_for_status()
    return r.json()

def update_note(id_token: str, note_id: str, title: str, content: str):
    payload = {}
    if title is not None:
        payload["title"] = title
    if content is not None:
        payload["content"] = content
    r = requests.put(
        f"{API_BASE}/notes/{note_id}",
        json=payload,
        headers={"Authorization": f"Bearer {id_token}"}
    )
    r.raise_for_status()
    return r.json()

def delete_note(id_token: str, note_id: str):
    r = requests.delete(
        f"{API_BASE}/notes/{note_id}",
        headers={"Authorization": f"Bearer {id_token}"}
    )
    r.raise_for_status()
    return r.json()

