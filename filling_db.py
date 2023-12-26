import requests
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

BASE_URL = "http://127.0.0.1:5000"


def create_project():
    project_data = {
        "name": fake.word(),
        "code": fake.uuid4(),
        "complexity": random.randint(1, 10),
        "deadline": (datetime.now() + timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
    }
    response = requests.post(f"{BASE_URL}/projects", json=project_data)
    return response.json().get("project", {}).get("id")


def create_employee():
    employee_data = {
        "position": fake.job(),
        "full_name": fake.name(),
        "identifier": fake.uuid4(),
    }
    response = requests.post(f"{BASE_URL}/employees", json=employee_data)
    return response.json().get("employee", {}).get("id")


def create_assignment(project_id, employee_id):
    assignment_data = {
        "project_id": project_id,
        "employee_id": employee_id,
        "issue_date": fake.date_this_decade().strftime("%Y-%m-%d"),
        "complexity": random.randint(1, 10),
        "planned_completion_date": (datetime.now() + timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
        "actual_completion_date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
    }
    response = requests.post(f"{BASE_URL}/assignments", json=assignment_data)
    return response.json().get("assignment", {}).get("id")


for _ in range(100):
    project_id = create_project()
    employee_id = create_employee()
    create_assignment(project_id, employee_id)

print("Database filled successfully.")
