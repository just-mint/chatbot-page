import toml
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path

def _load_secrets():
    secrets_path = Path(__file__).parents[3] / ".streamlit" / "secrets.toml"
    return toml.load(secrets_path)

def get_pyrebase_auth():
    secrets = _load_secrets()
    firebase_cfg = secrets["firebase_client"]
    firebase_app = pyrebase.initialize_app(firebase_cfg)
    return firebase_app.auth()

def init_firebase_admin():
    if not firebase_admin._apps:
        secrets = _load_secrets()
        cred_dict = secrets["firebase_admin"]
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

def get_firestore():
    init_firebase_admin()
    return firestore.client()