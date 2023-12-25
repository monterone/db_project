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
        return jsonify({"message": "Project created successfully", "project": data}), 200
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


@app.route("/projects", methods=["GET"])
def get_all_projects():
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
def get_project_by_id(project_id):
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
    role = data.get('role')

    if not all([project_id, employee_id, role]):
        return jsonify({'error': 'Missing data in the request'}), 400

    with DBSession() as session:
        project = session.query(Project).get(project_id)
        employee = session.query(Employee).get(employee_id)

        if not project or not employee:
            return jsonify({'error': 'Project or employee not found'}), 404

        assignment = Assignment(project=project, employee=employee, role=role)

        try:
            session.add(assignment)
            session.commit()
            return jsonify({'message': 'Assignment created successfully', 'assignment': assignment.serialize()}), 201
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
    new_role = data.get('role')

    assignment = session.query(Assignment).get(assignment_id)

    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    if new_role:
        assignment.role = new_role

    try:
        session.commit()
        return jsonify({'message': 'Assignment updated successfully', 'assignment': assignment.serialize()})
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
        return jsonify({'message': 'Assignment deleted successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
