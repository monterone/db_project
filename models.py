from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    code = Column(String, index=True)
    complexity = Column(Integer)
    deadline = Column(Date)
    assignments = relationship("Assignment", back_populates="project")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "complexity": self.complexity,
            "deadline": str(self.deadline) if self.deadline else None,
        }


class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    issue_date = Column(Date)
    complexity = Column(Integer)
    planned_completion_date = Column(Date)
    actual_completion_date = Column(Date)

    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="assignments")

    employee_id = Column(Integer, ForeignKey("employees.id"))
    employee = relationship("Employee", back_populates="assignments")

    def serialize(self):
        return {
            'id': self.id,
            'issue_date': str(self.issue_date) if self.issue_date else None,
            'complexity': self.complexity,
            'planned_completion_date': str(self.planned_completion_date) if self.planned_completion_date else None,
            'actual_completion_date': str(self.actual_completion_date) if self.actual_completion_date else None,
            'project': self.project.serialize(),
            'employee': self.employee.serialize()
        }


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    position = Column(String)
    full_name = Column(String)
    identifier = Column(String, unique=True)
    assignments = relationship("Assignment", back_populates="employee")

    def serialize(self):
        return {
            'id': self.id,
            'position': self.position,
            'full_name': self.full_name,
            'identifier': self.identifier,
        }


