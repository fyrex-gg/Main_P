import json
import datetime
import csv
import os
import matplotlib.pyplot as plt

# File paths
JSON_FILE_PATH = "tasks.json"
CSV_FILE_PATH = "tasks.csv"

# Constants
MENU_OPTIONS = [
    "View Tasks",
    "Add a Task",
    "Edit a Task",
    "Delete a Task",
    "Mark Task as Completed",
    "View Statistics",
    "Import Tasks",
    "Export Tasks",
    "Exit"
]

# Helper Functions
def calculate_priority(task):
    score = 0
    if task.importance == "high":
        score += 50
    elif task.importance == "medium":
        score += 30
    else:
        score += 10

    days_to_deadline = (datetime.datetime.strptime(task.deadline, "%Y-%m-%d %H:%M") - datetime.datetime.now()).days
    score += max(0, 40 - days_to_deadline)  # Higher scores for closer deadlines

    if task.estimated_time < 2:
        score += 10  # Bonus for quick tasks
    return score

def load_tasks_from_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            return [Task(**task) for task in data]
    return []

def save_tasks_to_file(tasks, file_path):
    with open(file_path, 'w') as file:
        json.dump([task.__dict__ for task in tasks], file, indent=4)

def import_tasks_from_csv(file_path):
    tasks = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["estimated_time"] = int(row["estimated_time"])
            row["completed"] = row["completed"].lower() == "true"
            tasks.append(Task(**row))
    return tasks

def export_tasks_to_csv(tasks, file_path):
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["id", "title", "description", "deadline", "estimated_time", "importance", "completed"])
        writer.writeheader()
        writer.writerows([task.__dict__ for task in tasks])

def plot_statistics(tasks):
    completed_tasks = sum(1 for task in tasks if task.completed)
    overdue_tasks = sum(
        1 for task in tasks if not task.completed and datetime.datetime.strptime(task.deadline, "%Y-%m-%d %H:%M") < datetime.datetime.now()
    )
    pending_tasks = len(tasks) - completed_tasks - overdue_tasks

    labels = ['Completed', 'Overdue', 'Pending']
    sizes = [completed_tasks, overdue_tasks, pending_tasks]
    colors = ['green', 'red', 'yellow']
    _, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('Task Statistics')
    plt.show()  # Ensures the plot is displayed

# Classes
class Task:
    def __init__(self, id, title, description, deadline, estimated_time, importance, completed=False):
        self.id = id
        self.title = title
        self.description = description
        self.deadline = deadline
        self.estimated_time = estimated_time
        self.importance = importance
        self.completed = completed

    def mark_completed(self):
        self.completed = True

class ToDoList:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def edit_task(self, task_id, updated_task):
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks[i] = updated_task
                return

    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def view_tasks(self, filter_by=None):
        if filter_by:
            return [task for task in self.tasks if task.importance == filter_by]
        return self.tasks

    def get_statistics(self):
        completed_tasks = sum(1 for task in self.tasks if task.completed)
        overdue_tasks = sum(1 for task in self.tasks if not task.completed and datetime.datetime.strptime(task.deadline, "%Y-%m-%d %H:%M") < datetime.datetime.now())
        return {
            "completed": completed_tasks,
            "overdue": overdue_tasks,
            "total": len(self.tasks)
        }

# Main Menu
def display_menu():
    for i, option in enumerate(MENU_OPTIONS, 1):
        print(f"{i}. {option}")

def handle_menu_selection(choice, to_do_list):
    if choice == '1':
        tasks = to_do_list.view_tasks()
        for task in tasks:
            print(vars(task))
    elif choice == '2':
        id = len(to_do_list.tasks) + 1
        title = input("Title: ")
        description = input("Description: ")
        deadline = input("Deadline (YYYY-MM-DD HH:MM): ")
        estimated_time = int(input("Estimated Time (hours): "))
        importance = input("Importance (high/medium/low): ")
        task = Task(id, title, description, deadline, estimated_time, importance)
        to_do_list.add_task(task)
    elif choice == '3':
        task_id = int(input("Task ID to edit: "))
        title = input("Title: ")
        description = input("Description: ")
        deadline = input("Deadline (YYYY-MM-DD HH:MM): ")
        estimated_time = int(input("Estimated Time (hours): "))
        importance = input("Importance (high/medium/low): ")
        updated_task = Task(task_id, title, description, deadline, estimated_time, importance)
        to_do_list.edit_task(task_id, updated_task)
    elif choice == '4':
        task_id = int(input("Task ID to delete: "))
        to_do_list.delete_task(task_id)
    elif choice == '5':
        task_id = int(input("Task ID to mark as completed: "))
        for task in to_do_list.tasks:
            if task.id == task_id:
                task.mark_completed()
                break
    elif choice == '6':
        stats = to_do_list.get_statistics()
        print(f"Completed: {stats['completed']}, Overdue: {stats['overdue']}, Total: {stats['total']}")
        plot_statistics(to_do_list.tasks)
    elif choice == '7':
        imported_tasks = import_tasks_from_csv(CSV_FILE_PATH)
        to_do_list.tasks.extend(imported_tasks)
    elif choice == '8':
        export_tasks_to_csv(to_do_list.tasks, CSV_FILE_PATH)
    elif choice == '9':
        print("Exiting...")
        exit()

# Main Program
def main():
    to_do_list = ToDoList()
    to_do_list.tasks = load_tasks_from_file(JSON_FILE_PATH)

    while True:
        display_menu()
        choice = input("Select an option: ")
        handle_menu_selection(choice, to_do_list)
        save_tasks_to_file(to_do_list.tasks, JSON_FILE_PATH)

if __name__ == "__main__":
    main()
