import streamlit as st
import pandas as pd
from datetime import datetime

# Constants for file paths
CSV_FILE = "tasks.csv"
COMPLETED_TASKS_FILE = "completed_tasks.csv"

# Initialize CSV files with headers if they don't exist
def initialize_csv():
    for file in [CSV_FILE, COMPLETED_TASKS_FILE]:
        try:
            pd.read_csv(file)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["title", "category", "priority", "deadline", "status"])
            df.to_csv(file, index=False)

# Load tasks
def load_tasks(show_completed=False):
    file = COMPLETED_TASKS_FILE if show_completed else CSV_FILE
    try:
        return pd.read_csv(file)
    except FileNotFoundError:
        return pd.DataFrame(columns=["title", "category", "priority", "deadline", "status"])

# Save tasks
def save_tasks(df, completed=False):
    file = COMPLETED_TASKS_FILE if completed else CSV_FILE
    df.to_csv(file, index=False)

# Add a new task
def add_task():
    with st.form("add_task_form"):
        title = st.text_input("Task Title")
        category = st.selectbox("Category", ["Work", "Personal", "School", "Others"])
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        deadline_date = st.date_input("Deadline Date")
        deadline_time = st.time_input("Deadline Time")
        submit = st.form_submit_button("Add Task")

        if submit:
            deadline = f"{deadline_date} {deadline_time}"
            task = pd.DataFrame([{
                "title": title,
                "category": category,
                "priority": priority,
                "deadline": deadline,
                "status": "Pending"
            }])
            df = load_tasks()
            df = pd.concat([df, task], ignore_index=True)
            save_tasks(df)
            st.success("Task added successfully!")

# View tasks
def view_tasks(show_completed=False):
    df = load_tasks(show_completed=show_completed)
    if df.empty:
        st.info("No tasks to display.")
    else:
        st.write(df)

# Delete task
def delete_task():
    df = load_tasks()
    task_titles = df["title"].tolist()
    selected_task = st.selectbox("Select Task to Delete", task_titles)
    if st.button("Delete Task"):
        df = df[df["title"] != selected_task]
        save_tasks(df)
        st.success("Task deleted successfully!")

# Modify task
def modify_task():
    df = load_tasks()
    task_titles = df["title"].tolist()
    selected_task = st.selectbox("Select Task to Modify", task_titles)
    task = df[df["title"] == selected_task].iloc[0]

    with st.form("modify_task_form"):
        new_title = st.text_input("Task Title", task["title"])
        new_category = st.selectbox("Category", ["Work", "Personal", "School", "Others"], index=["Work", "Personal", "School", "Others"].index(task["category"]))
        new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(task["priority"]))
        deadline_date, deadline_time = task["deadline"].split(" ")
        new_deadline_date = st.date_input("Deadline Date", datetime.strptime(deadline_date, '%Y-%m-%d').date())
        new_deadline_time = st.time_input("Deadline Time", datetime.strptime(deadline_time, '%H:%M').time())
        submit = st.form_submit_button("Modify Task")

        if submit:
            df.loc[df["title"] == selected_task, ["title", "category", "priority", "deadline"]] = [new_title, new_category, new_priority, f"{new_deadline_date} {new_deadline_time}"]
            save_tasks(df)
            st.success("Task modified successfully!")

# Mark task as completed
def mark_task_done():
    df = load_tasks()
    task_titles = df[df["status"] != "Done"]["title"].tolist()
    selected_task = st.selectbox("Select Task to Mark as Complete", task_titles)

    if st.button("Mark as Complete"):
        df.loc[df["title"] == selected_task, "status"] = "Done"
        completed_df = df[df["title"] == selected_task]
        df = df[df["title"] != selected_task]
        save_tasks(df)
        save_tasks(load_tasks(True).append(completed_df), completed=True)
        st.success("Task marked as complete!")

# Filter tasks
def filter_tasks():
    df = load_tasks()
    category = st.selectbox("Filter by Category", ["All", "Work", "Personal", "School", "Others"])
    priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    if category != "All":
        df = df[df["category"] == category]
    if priority != "All":
        df = df[df["priority"] == priority]
    st.write(df if not df.empty else "No tasks found for the selected filters.")

# Sort tasks
def sort_tasks():
    df = load_tasks()
    sort_by = st.selectbox("Sort By", ["title", "category", "priority", "deadline", "status"])
    df = df.sort_values(by=sort_by)
    st.write(df)

# Streamlit App
def main():
    st.title("Task Manager")

    menu_options = ["Add Task", "View Tasks", "Delete Task", "Modify Task", "Mark Task as Complete", "View Completed Tasks", "Filter Tasks", "Sort Tasks"]
    choice = st.sidebar.selectbox("Menu", menu_options)

    initialize_csv()  # Ensure CSV files are initialized

    if choice == "Add Task":
        add_task()
    elif choice == "View Tasks":
        view_tasks()
    elif choice == "Delete Task":
        delete_task()
    elif choice == "Modify Task":
        modify_task()
    elif choice == "Mark Task as Complete":
        mark_task_done()
    elif choice == "View Completed Tasks":
        view_tasks(show_completed=True)
    elif choice == "Filter Tasks":
        filter_tasks()
    elif choice == "Sort Tasks":
        sort_tasks()

if __name__ == "__main__":
    main()
