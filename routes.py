from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Project, Assignment, Employee


app = Flask(__name__)

DATABASE_URL = "postgresql://postgres:postgres1337@localhost:5432/"
DB_NAME = "project_management_db"

engine = create_engine(f"{DATABASE_URL}{DB_NAME}")
Base.metadata.bind = engine
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)


@app.route("/projects", methods=["POST"])
def create_project():
    session = DBSession()
    try:
        data = request.json
        project = Project(**data)
        session.add(project)
        session.commit()
        serialized_project = project.serialize()
        return jsonify({"message": "Project created successfully", "project": serialized_project}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route("/projects", methods=["GET"])
def get_projects():
    session = DBSession()
    try:
        projects = session.query(Project).all()
        project_list = [{"id": project.id, "name": project.name, "code": project.code, "complexity": project.complexity,
                         "deadline": str(project.deadline)} for project in projects]
        return jsonify({"projects": project_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route("/projects/<int:project_id>", methods=["GET"])
def get_project(project_id):
    session = DBSession()
    try:
        project = session.query(Project).filter_by(id=project_id).first()
        if project:
            return jsonify({"project": {"id": project.id, "name": project.name, "code": project.code,
                                        "complexity": project.complexity, "deadline": str(project.deadline)}}), 200
        else:
            return jsonify({"message": "Project not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route("/projects/<int:project_id>", methods=["PUT"])
def update_project(project_id):
    session = DBSession()
    try:
        project = session.query(Project).filter_by(id=project_id).first()
        if project:
            data = request.json
            project.name = data.get("name", project.name)
            project.code = data.get("code", project.code)
            project.complexity = data.get("complexity", project.complexity)
            project.deadline = data.get("deadline", project.deadline)
            session.commit()
            return jsonify({"message": "Project updated successfully",
                            "project": {"id": project.id, "name": project.name, "code": project.code,
                                        "complexity": project.complexity, "deadline": str(project.deadline)}}), 200
        else:
            return jsonify({"message": "Project not found"}), 404
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route("/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    session = DBSession()
    try:
        project = session.query(Project).get(project_id)
        if project:
            session.delete(project)
            session.commit()
            return jsonify({"message": f"Project with id {project_id} deleted successfully"}), 200
        else:
            return jsonify({"error": f"Project with id {project_id} not found"}), 404
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route('/assignments', methods=['POST'])
def create_assignment():
    data = request.get_json()
    project_id = data.get('project_id')
    employee_id = data.get('employee_id')
    issue_date = data.get('issue_date')
    complexity = data.get('complexity')
    planned_completion_date = data.get('planned_completion_date')
    actual_completion_date = data.get('actual_completion_date')

    if not all([project_id, employee_id, issue_date, complexity, planned_completion_date, actual_completion_date]):
        return jsonify({'error': 'Missing data in the request'}), 400

    with DBSession() as session:
        project = session.query(Project).get(project_id)
        employee = session.query(Employee).get(employee_id)

        if not project or not employee:
            return jsonify({'error': 'Project or employee not found'}), 404

        assignment = Assignment(
            project=project,
            employee=employee,
            issue_date=issue_date,
            complexity=complexity,
            planned_completion_date=planned_completion_date,
            actual_completion_date=actual_completion_date
        )

        try:
            session.add(assignment)
            session.commit()
            serialized_assignment = assignment.serialize()
            return jsonify({'assignment': serialized_assignment, 'message': 'Assignment created successfully'}), 200
        except Exception as e:
            session.rollback()
            return jsonify({'error': str(e)}), 500


@app.route('/assignments', methods=['GET'])
def get_assignments():
    session = DBSession()
    assignments = session.query(Assignment).all()
    return jsonify({'assignments': [assignment.serialize() for assignment in assignments]})


@app.route('/assignments/<int:assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    session = DBSession()
    assignment = session.query(Assignment).get(assignment_id)

    if assignment:
        return jsonify({'assignment': assignment.serialize()})
    else:
        return jsonify({'error': 'Assignment not found'}), 404


@app.route('/assignments/<int:assignment_id>', methods=['PUT'])
def update_assignment(assignment_id):
    session = DBSession()

    data = request.get_json()

    assignment = session.query(Assignment).get(assignment_id)

    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    assignment.issue_date = data.get('issue_date', assignment.issue_date)
    assignment.complexity = data.get('complexity', assignment.complexity)
    assignment.planned_completion_date = data.get('planned_completion_date', assignment.planned_completion_date)
    assignment.actual_completion_date = data.get('actual_completion_date', assignment.actual_completion_date)

    try:
        session.commit()
        return jsonify({'message': 'Assignment updated successfully', 'assignment': assignment.serialize()}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/assignments/<int:assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    session = DBSession()

    assignment = session.query(Assignment).get(assignment_id)

    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    try:
        session.delete(assignment)
        session.commit()
        return jsonify({'message': 'Assignment deleted successfully'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/employees', methods=['POST'])
def create_employee():
    session = DBSession()

    data = request.get_json()
    position = data.get('position')
    full_name = data.get('full_name')
    identifier = data.get('identifier')

    if not position or not full_name or not identifier:
        return jsonify({'error': 'Missing data in the request'}), 400

    employee = Employee(position=position, full_name=full_name, identifier=identifier)

    try:
        session.add(employee)
        session.commit()
        return jsonify({'message': 'Employee created successfully', 'employee': employee.serialize()}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/employees', methods=['GET'])
def get_employees():
    session = DBSession()
    employees = session.query(Employee).all()
    serialized_employees = [employee.serialize() for employee in employees]
    return jsonify({'employees': serialized_employees})


@app.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    session = DBSession()
    employee = session.query(Employee).get(employee_id)

    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    return jsonify({'employee': employee.serialize()})


@app.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    session = DBSession()

    employee = session.query(Employee).get(employee_id)

    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    data = request.get_json()
    full_name = data.get('full_name')
    position = data.get('position')

    if not full_name or not position:
        return jsonify({'error': 'Missing data in the request'}), 400

    employee.full_name = full_name
    employee.position = position

    try:
        session.commit()
        return jsonify({'message': 'Employee updated successfully', 'employee': employee.serialize()}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    session = DBSession()

    employee = session.query(Employee).get(employee_id)

    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    try:
        session.delete(employee)
        session.commit()
        return jsonify({'message': 'Employee deleted successfully'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


if __name__ == "__main__":
    app.run(debug=True)
