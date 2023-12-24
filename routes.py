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
        project_list = [{"id": project.id, "name": project.name, "code": project.code, "complexity": project.complexity, "deadline": str(project.deadline)} for project in projects]
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
            return jsonify({"project": {"id": project.id, "name": project.name, "code": project.code, "complexity": project.complexity, "deadline": str(project.deadline)}}), 200
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
            return jsonify({"message": "Project updated successfully", "project": {"id": project.id, "name": project.name, "code": project.code, "complexity": project.complexity, "deadline": str(project.deadline)}}), 200
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


if __name__ == "__main__":
    app.run(debug=True)
