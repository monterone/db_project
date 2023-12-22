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


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    position = Column(String)
    full_name = Column(String)
    identifier = Column(String, unique=True)
    assignments = relationship("Assignment", back_populates="employee")

