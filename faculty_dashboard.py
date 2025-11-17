import streamlit as st
from backend import (
    get_connection, get_teacher_notifications, post_teacher_notification
)

def faculty_dashboard(fid):
    conn, cur = get_connection()
    row = cur.execute("SELECT name, subject FROM faculty WHERE faculty_id=?", (fid,)).fetchone()
    if not row:
        st.error("Faculty not found")
        return

    name, subject = row
    st.title(f"Faculty Dashboard ({name} - {subject})")

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    menu = st.sidebar.radio("Menu", [
        "Mark Attendance", "Enter Marks",
        "Post Notification", "View Notifications",
        "Change Password"
    ])

    # MARK ATTENDANCE
    if menu == "Mark Attendance":
        st.header("Mark Attendance")
        section = st.selectbox("Section", ["A", "B"])

        cur.execute("SELECT roll_no,name FROM students WHERE section=?", (section,))
        students = cur.fetchall()

        marked = {}
        for r, n in students:
            marked[r] = st.checkbox(f"{r} - {n}", value=True)

        if st.button("Submit"):
            import datetime
            date = str(datetime.date.today())
            for r, present in marked.items():
                cur.execute(
                    "INSERT INTO attendance VALUES (?,?,?,?,?)",
                    (r, fid, subject, date, "Present" if present else "Absent")
                )
            conn.commit()
            st.success("Saved")

    # ENTER MARKS
    if menu == "Enter Marks":
        st.header("Enter Marks")
        exam = st.selectbox("Exam", ["Mid-term", "End-term"])
        section = st.selectbox("Section", ["A", "B"])

        cur.execute("SELECT roll_no,name FROM students WHERE section=?", (section,))
        students = cur.fetchall()

        marks_input = {}
        for r, n in students:
            marks_input[r] = st.number_input(f"{r} - {n}", 0, 100)

        if st.button("Save"):
            for r, m in marks_input.items():
                cur.execute("INSERT INTO marks VALUES (?,?,?,?,?)",
                            (r, subject, exam, m, fid))
            conn.commit()
            st.success("Marks submitted")

    # POST NOTIF
    if menu == "Post Notification":
        title = st.text_input("Title")
        msg = st.text_area("Message")
        if st.button("Post"):
            post_teacher_notification(fid, subject, title, msg)
            st.success("Notification posted")

    # VIEW NOTIFS
    if menu == "View Notifications":
        st.header("Your Notifications + Admin")
        rows = get_teacher_notifications(fid)
        for t, m, ts, pb, tid, sub in rows:
            st.markdown(f"**[{ts}] {t} ({pb})**")
            st.info(m)

    # CHANGE PASSWORD
    if menu == "Change Password":
        old = st.text_input("Old Password", type="password")
        new = st.text_input("New Password", type="password")
        conf = st.text_input("Confirm", type="password")

        if st.button("Update"):
            c2, ucur = get_connection()
            pw = ucur.execute("SELECT password FROM login_credentials WHERE user_id=?", (fid,)).fetchone()[0]
            if pw == old and new == conf:
                ucur.execute("UPDATE login_credentials SET password=? WHERE user_id=?", (new, fid))
                c2.commit()
                st.success("Updated")
            else:
                st.error("Wrong old password")

    conn.close()
