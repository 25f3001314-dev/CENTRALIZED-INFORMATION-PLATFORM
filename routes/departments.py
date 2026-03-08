from flask import Blueprint, jsonify
from models.department import Department
from models.officer import Officer
from utils.helpers import format_response

departments_bp = Blueprint('departments', __name__)


@departments_bp.route('/api/departments', methods=['GET'])
def list_departments():
    depts = Department.query.all()
    return jsonify(format_response([d.to_dict() for d in depts]))


@departments_bp.route('/api/departments/<int:dept_id>/officers', methods=['GET'])
def dept_officers(dept_id):
    dept = Department.query.get_or_404(dept_id)
    officers = Officer.query.filter_by(department=dept.name).all()
    return jsonify(format_response([o.to_dict() for o in officers]))
