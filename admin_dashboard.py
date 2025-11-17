import streamlit as st
from backend import (
    get_connection, generate_roll_no, generate_faculty_id,
    generate_password, post_admin_notification
)

def admin_dashboard():
    st.title("🏫 Admin Dashboard")

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    menu = st.sidebar.radio("Menu", [
        "Add Student", "Add Faculty", "View Students", "View Faculty",
        "Post Notification", "Update Student Info", "Reset Database"
    ])

    conn, cur = get_connection()

    # Add Student
    if menu == "Add Student":
        st.header("Add Student")
        name = st.text_input("Name")
        section = st.selectbox("Section", ["A", "B"])
        year = st.number_input("Year", 1, 4)

        if st.button("Add"):
            roll = generate_roll_no()
            passwd = generate_password("stu")

            cur.execute("INSERT INTO students VALUES (?,?,?,?,?)",
                        (roll, name, "B.Tech CSE", year, section))
            cur.execute("INSERT INTO login_credentials VALUES (?,?,?,?)",
                        (roll, passwd, "student", 1))
            conn.commit()
            st.success(f"Added {roll} | Password: {passwd}")

    # Add Faculty
    if menu == "Add Faculty":
        st.header("Add Faculty")
        name = st.text_input("Name")
        subject = st.selectbox("Subject", ["OS", "DBMS"])

        if st.button("Add Faculty"):
            fid = generate_faculty_id()
            passwd = generate_password("fac")

            cur.execute("INSERT INTO faculty VALUES (?,?,?)", (fid, name, subject))
            cur.execute("INSERT INTO login_credentials VALUES (?,?,?,?)",
                        (fid, passwd, "faculty", 1))
            conn.commit()
            st.success(f"Added {fid} | Password: {passwd}")

    # View Students
    if menu == "View Students":
        st.header("All Students")
        rows = cur.execute("SELECT * FROM students").fetchall()
        st.dataframe(rows)

    # View faculty
    if menu == "View Faculty":
        st.header("All Faculty")
        rows = cur.execute("SELECT * FROM faculty").fetchall()
        st.dataframe(rows)

    # Post notification
    if menu == "Post Notification":
        title = st.text_input("Title")
        msg = st.text_area("Message")
        if st.button("Post"):
            post_admin_notification(title, msg)
            st.success("Notification sent")

    # Update student
    if menu == "Update Student Info":
        st.header("Update Student Info")
        rolls = [r[0] for r in cur.execute("SELECT roll_no FROM students")]
        if rolls:
            selected = st.selectbox("Select Roll", rolls)
            row = cur.execute("SELECT name,course,year,section FROM students WHERE roll_no=?", (selected,)).fetchone()
            name = st.text_input("Name", row[0])
            course = st.text_input("Course", row[1])
            year = st.number_input("Year", 1, 4, value=row[2])
            section = st.selectbox("Section", ["A","B"], index=["A","B"].index(row[3]))

            if st.button("Update"):
                cur.execute("UPDATE students SET name=?,course=?,year=?,section=? WHERE roll_no=?",
                            (name, course, year, section, selected))
                conn.commit()
                st.success("Updated")

    # Reset DB
    if menu == "Reset Database":
        if st.button("Delete All Data"):
            cur.execute("DELETE FROM students")
            cur.execute("DELETE FROM faculty")
            cur.execute("DELETE FROM marks")
            cur.execute("DELETE FROM attendance")
            cur.execute("DELETE FROM notifications")
            cur.execute("DELETE FROM login_credentials WHERE user_id!='admin'")
            conn.commit()
            st.success("All data cleared")

    conn.close()
