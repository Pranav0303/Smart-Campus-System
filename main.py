import streamlit as st
from backend import setup_database, login_user, update_password
from admin_dashboard import admin_dashboard
from faculty_dashboard import faculty_dashboard
from student_dashboard import student_dashboard

def main():
    st.set_page_config(page_title="Smart Campus System", page_icon="🏫", layout="wide")
    setup_database()

    st.title("🏫 SMART CAMPUS SYSTEM")

    if "role" not in st.session_state:
        uid = st.text_input("User ID")
        pw = st.text_input("Password", type="password")

        if st.button("Login"):
            role, first = login_user(uid, pw)
            if role:
                st.session_state.user_id = uid
                st.session_state.role = role
                st.session_state.first_login = first
                st.rerun()
            else:
                st.error("Invalid credentials")

    else:
        uid = st.session_state.user_id
        role = st.session_state.role

        # FIRST LOGIN PASSWORD RESET
        if st.session_state.first_login:
            new = st.text_input("New Password", type="password")
            conf = st.text_input("Confirm Password", type="password")
            if st.button("Update"):
                if new == conf:
                    update_password(uid, new)
                    st.session_state.clear()
                    st.success("Password updated. Login again.")
                    st.rerun()
                else:
                    st.error("Passwords do not match")

        else:
            if role == "admin":
                admin_dashboard()
            elif role == "faculty":
                faculty_dashboard(uid)
            elif role == "student":
                student_dashboard(uid)
            else:
                st.error("Role not recognized")

if __name__ == "__main__":
    main()
