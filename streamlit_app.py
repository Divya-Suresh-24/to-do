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
            if title.strip() == "":
                st.error("Task Title cannot be empty.")
                return

            # Check for duplicate task titles
            existing_tasks = load_tasks()
            if title in existing_tasks["title"].values:
                st.warning("A task with this title already exists. Please use a unique title.")
                return

            # Add the task
            deadline = f"{deadline_date} {deadline_time}"
            task = pd.DataFrame([{
                "title": title,
                "category": category,
                "priority": priority,
                "deadline": deadline,
                "status": "Pending"
            }])
            updated_tasks = pd.concat([existing_tasks, task], ignore_index=True)
            save_tasks(updated_tasks)
            st.success("Task added successfully!")

# Modify a specific task
def modify_task_specific(task_title):
    df = load_tasks()
    task = df[df["title"] == task_title].iloc[0]

    with st.form(f"modify_task_form_{task_title}"):
        st.subheader(f"Modify Task: {task_title}")
        new_title = st.text_input("Title", value=task["title"])
        new_category = st.selectbox("Category", ["Work", "Personal", "School", "Others"], index=["Work", "Personal", "School", "Others"].index(task["category"]))
        new_priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(task["priority"]))

        deadline_date = None
        deadline_time = None
        if task["deadline"] and task["deadline"] != "None":
            try:
                deadline_parts = task["deadline"].split(" ")
                deadline_date = datetime.strptime(deadline_parts[0], "%Y-%m-%d").date()
                if len(deadline_parts) > 1:
                    deadline_time = datetime.strptime(deadline_parts[1], "%H:%M:%S").time()
            except ValueError:
                st.warning("Invalid deadline format. Please update it.")

        new_deadline_date = st.date_input("Deadline Date", value=deadline_date)
        new_deadline_time = st.time_input("Deadline Time", value=deadline_time)

        submit = st.form_submit_button("Save Changes")
        if submit:
            new_deadline = f"{new_deadline_date} {new_deadline_time}" if new_deadline_date and new_deadline_time else "None"
            df.loc[df["title"] == task_title, ["title", "category", "priority", "deadline"]] = [new_title, new_category, new_priority, new_deadline]
            save_tasks(df)
            st.success(f"Task '{task_title}' updated successfully!")
            st.rerun()  # Refresh UI

# Mark a specific task as completed
def mark_task_done_specific(task_title):
    df = load_tasks()
    task = df[df["title"] == task_title]
    if not task.empty:
        df = df[df["title"] != task_title]
        save_tasks(df)
        completed_df = load_tasks(show_completed=True)
        completed_df = pd.concat([completed_df, task], ignore_index=True)
        save_tasks(completed_df, completed=True)
        st.success(f"Task '{task_title}' marked as complete!")
        st.rerun()  # Refresh UI

# Mark a specific task as pending
def mark_task_pending_specific(task_title):
    completed_df = load_tasks(show_completed=True)
    task = completed_df[completed_df["title"] == task_title]
    if not task.empty:
        completed_df = completed_df[completed_df["title"] != task_title]
        save_tasks(completed_df, completed=True)
        pending_df = load_tasks()
        pending_df = pd.concat([pending_df, task], ignore_index=True)
        save_tasks(pending_df)
        st.success(f"Task '{task_title}' marked as pending!")
        st.rerun()  # Refresh UI

# Delete a specific task
def delete_task_specific(task_title, completed=False):
    df = load_tasks(show_completed=completed)
    df = df[df["title"] != task_title]
    save_tasks(df, completed=completed)
    st.success(f"Task '{task_title}' deleted successfully!")
    st.rerun()  # Refresh UI

# View tasks
def view_tasks(show_completed=False):
    df = load_tasks(show_completed=show_completed)
    if df.empty:
        st.info("No tasks to display.")
    else:
        for index, row in df.iterrows():
            unique_key = f"{index}_{row['title']}_{'completed' if show_completed else 'pending'}"
            st.write(f"**Title:** {row['title']}")
            st.write(f"**Category:** {row['category']}")
            st.write(f"**Priority:** {row['priority']}")
            st.write(f"**Deadline:** {row['deadline']}")
            st.write(f"**Status:** {row['status']}")

            if show_completed:
                if st.button("Mark as Pending", key=f"pending_{unique_key}"):
                    mark_task_pending_specific(row["title"])
            else:
                if st.button("Mark as Complete", key=f"complete_{unique_key}"):
                    mark_task_done_specific(row["title"])
                if st.button("Modify", key=f"modify_{unique_key}"):
                    modify_task_specific(row["title"])
            if st.button("Delete", key=f"delete_{unique_key}"):
                delete_task_specific(row["title"], completed=show_completed)

            st.write("---")

# Streamlit App
def main():
    st.title("Task Manager")
    initialize_csv()

    tab1, tab2, tab3 = st.tabs(["Add New Task", "View Tasks", "View Completed Tasks"])
    with tab1:
        add_task()
    with tab2:
        view_tasks()
    with tab3:
        view_tasks(show_completed=True)

if __name__ == "__main__":
    main()
