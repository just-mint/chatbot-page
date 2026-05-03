import requests
import streamlit as st

from api_client import signup, login, google_login, get_notes, create_note, update_note, delete_note

st.set_page_config(page_title="Notes App", page_icon="📝")

# ── Session state ─────────────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "notes" not in st.session_state:
    st.session_state.notes = []
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False
if "editing_note" not in st.session_state:
    st.session_state.editing_note = None  # note id being edited


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_notes():
    if not st.session_state.user:
        return
    try:
        st.session_state.notes = get_notes(st.session_state.user["idToken"])
    except Exception:
        st.session_state.notes = []


def clear_google_params():
    try:
        st.query_params.clear()
    except Exception:
        pass


# ── Google OAuth callback ─────────────────────────────────────────────────────

def handle_google_callback():
    if st.session_state.user:
        return
    params = st.query_params
    raw_token = params.get("id_token")
    if not raw_token:
        return
    id_token = raw_token[0] if isinstance(raw_token, list) else raw_token
    try:
        user = google_login(id_token)
        st.session_state.user = user
        load_notes()
        clear_google_params()
        st.success("Đăng nhập Google thành công")
        st.rerun()
    except requests.HTTPError as e:
        st.error(f"Đăng nhập Google thất bại: {e}")
        clear_google_params()
    except Exception as e:
        st.error(f"Lỗi xử lý Google login: {e}")
        clear_google_params()


# ── Auth forms ────────────────────────────────────────────────────────────────

def login_form():
    st.subheader("Đăng nhập")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập")
        goto_signup = st.form_submit_button("Chưa có tài khoản? Đăng ký")

    if goto_signup:
        st.session_state.show_signup = True
        st.rerun()

    if submitted:
        try:
            user = login(email, password)
            st.session_state.user = user
            load_notes()
            st.success("Đăng nhập thành công")
            st.rerun()
        except requests.HTTPError as e:
            st.error(f"Đăng nhập thất bại: {e}")
        except Exception as e:
            st.error(f"Lỗi: {e}")

    st.markdown("### Hoặc")
    google_login_url = dict(st.secrets["google-login"]).get("google-url", "")
    if google_login_url:
        st.markdown(
            f'''<a href="{google_login_url}" target="_self" style="
                display:inline-block;width:100%;text-align:center;
                padding:0.6rem 1rem;background-color:white;color:black;
                text-decoration:none;border-radius:0.5rem;
                border:1px solid #ddd;font-weight:600;">
                Đăng nhập với Google
            </a>''',
            unsafe_allow_html=True,
        )


def signup_form():
    st.subheader("Đăng ký")
    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Tạo tài khoản")
        goto_login = st.form_submit_button("Đã có tài khoản? Đăng nhập")

    if goto_login:
        st.session_state.show_signup = False
        st.rerun()

    if submitted:
        try:
            signup(email, password)
            st.success("Tạo tài khoản thành công, hãy đăng nhập")
            st.session_state.show_signup = False
            st.rerun()
        except requests.HTTPError as e:
            st.error(f"Đăng ký thất bại: {e}")
        except Exception as e:
            st.error(f"Lỗi: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────

handle_google_callback()

st.title("📝 Notes App")

# Header: user info & logout
if st.session_state.user:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.success(f"Đang đăng nhập: {st.session_state.user['email']}")
    with col2:
        if st.button("Đăng xuất"):
            st.session_state.user = None
            st.session_state.notes = []
            st.session_state.editing_note = None
            clear_google_params()
            st.rerun()
else:
    if st.session_state.show_signup:
        signup_form()
    else:
        login_form()

st.divider()

# ── Notes UI (only when logged in) ───────────────────────────────────────────
if st.session_state.user:
    token = st.session_state.user["idToken"]

    # ── Create new note ───────────────────────────────────────────────────────
    st.subheader("✏️ Tạo ghi chú mới")
    with st.form("create_note_form", clear_on_submit=True):
        new_title = st.text_input("Tiêu đề")
        new_content = st.text_area("Nội dung", height=120)
        create_btn = st.form_submit_button("➕ Thêm ghi chú")

    if create_btn:
        if not new_title.strip():
            st.warning("Vui lòng nhập tiêu đề.")
        else:
            try:
                create_note(token, new_title.strip(), new_content.strip())
                st.success("Đã thêm ghi chú!")
                load_notes()
                st.rerun()
            except Exception as e:
                st.error(f"Lỗi: {e}")

    st.divider()

    # ── List notes ────────────────────────────────────────────────────────────
    st.subheader("📋 Danh sách ghi chú")

    if st.button("🔄 Tải lại"):
        load_notes()
        st.rerun()

    if not st.session_state.notes:
        st.info("Chưa có ghi chú nào. Hãy tạo ghi chú đầu tiên!")
    else:
        for note in st.session_state.notes:
            note_id = note["id"]
            with st.expander(f"📌 {note['title']}", expanded=False):
                # Edit mode
                if st.session_state.editing_note == note_id:
                    with st.form(f"edit_{note_id}"):
                        edit_title = st.text_input("Tiêu đề", value=note["title"])
                        edit_content = st.text_area("Nội dung", value=note["content"], height=150)
                        col_save, col_cancel = st.columns(2)
                        save_btn = col_save.form_submit_button("💾 Lưu")
                        cancel_btn = col_cancel.form_submit_button("❌ Hủy")

                    if save_btn:
                        try:
                            update_note(token, note_id, edit_title.strip(), edit_content.strip())
                            st.success("Đã cập nhật!")
                            st.session_state.editing_note = None
                            load_notes()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")

                    if cancel_btn:
                        st.session_state.editing_note = None
                        st.rerun()

                # View mode
                else:
                    st.markdown(note["content"] if note["content"] else "_Không có nội dung_")
                    if note.get("created_at"):
                        st.caption(f"🕐 {note['created_at'][:19].replace('T', ' ')}")

                    col_edit, col_del = st.columns([1, 1])
                    if col_edit.button("✏️ Sửa", key=f"edit_btn_{note_id}"):
                        st.session_state.editing_note = note_id
                        st.rerun()
                    if col_del.button("🗑️ Xóa", key=f"del_btn_{note_id}"):
                        try:
                            delete_note(token, note_id)
                            st.success("Đã xóa ghi chú!")
                            load_notes()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Lỗi: {e}")