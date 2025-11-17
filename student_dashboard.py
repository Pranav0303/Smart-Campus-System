import streamlit as st
from backend import (
    get_connection,
    get_admin_notifications, get_subject_notifications,
    update_password
)

def student_dashboard(roll):
    conn, cur = get_connection()
    row = cur.execute("SELECT name,course,year,section FROM students WHERE roll_no=?", (roll,)).fetchone()
    if not row:
        st.error("Student not found")
        return

    name, course, year, section = row
    st.title(f"Student Dashboard ({name})")

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    menu = st.sidebar.radio(
        "Menu",
        ["Admin Notifications", "OS Notifications", "DBMS Notifications",
         "View Marks", "View Attendance", "Change Password"]
    )

    # ADMIN NOTIFS
    if menu == "Admin Notifications":
        rows = get_admin_notifications()
        for t, m, ts, p in rows:
            st.markdown(f"**[{ts}] {t} (Admin)**")
            st.info(m)

    # SUBJECT NOTIFS
    if menu == "OS Notifications":
        rows = get_subject_notifications("OS")
        for t, m, ts, tid in rows:
            st.markdown(f"**[{ts}] {t} (Teacher: {tid})**")
            st.info(m)

    if menu == "DBMS Notifications":
        rows = get_subject_notifications("DBMS")
        for t, m, ts, tid in rows:
            st.markdown(f"**[{ts}] {t} (Teacher: {tid})**")
            st.info(m)

    # MARKS
    if menu == "View Marks":
        exam = st.selectbox("Exam", ["Mid-term", "End-term"])
        for sub in ["OS", "DBMS"]:
            res = cur.execute(
                "SELECT marks,faculty_id FROM marks WHERE roll_no=? AND subject=? AND exam_type=?",
                (roll, sub, exam)
            ).fetchone()

            if res:
                marks, fid = res
            else:
                marks, fid = 0, "N/A"

            st.markdown(f"**{sub}**")
            st.info(f"Marks: {marks}/100 | Faculty: {fid}")

    # ATTENDANCE
    if menu == "View Attendance":
        for sub in ["OS", "DBMS"]:
            total, present = cur.execute("""
                SELECT COUNT(*),
                SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END)
                FROM attendance WHERE roll_no=? AND subject=?
            """, (roll, sub)).fetchone()

            total = total or 0
            present = present or 0
            pct = (present / total * 100) if total else 0

            st.markdown(f"**{sub} Attendance**")
            st.info(f"{present}/{total} | {pct:.2f}%")

    # PASSWORD CHANGE
    if menu == "Change Password":
        old = st.text_input("Old Password", type="password")
        new = st.text_input("New Password", type="password")
        conf = st.text_input("Confirm Password", type="password")

        if st.button("Update"):
            pw = cur.execute("SELECT password FROM login_credentials WHERE user_id=?", (roll,)).fetchone()[0]
            if pw == old and new == conf:
                update_password(roll, new)
                st.success("Password updated")
            else:
                st.error("Wrong password")

    conn.close()
