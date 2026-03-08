from datetime import datetime, timedelta
import logging
from flask import Blueprint, request, jsonify
from models.issue import Issue
from models.officer import Officer
from models.department import Department
from models.rating import Rating
from models.ai_analysis import AIAnalysis
from models.escalation import EscalationLog
from utils.helpers import format_response
from sqlalchemy import func
from models import db

analytics_bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)


@analytics_bp.route('/api/analytics/dashboard', methods=['GET'])
def dashboard():
    total = Issue.query.count()
    active = Issue.query.filter(Issue.status.notin_(['Resolved', 'Closed'])).count()
    resolved = Issue.query.filter_by(status='Resolved').count()
    escalated = Issue.query.filter_by(escalated=True).count()

    resolved_issues = Issue.query.filter_by(status='Resolved').all()
    avg_resolution = 0
    if resolved_issues:
        total_days = sum(
            (i.updated_at - i.created_at).total_seconds() / 86400
            for i in resolved_issues if i.updated_at and i.created_at
        )
        avg_resolution = round(total_days / len(resolved_issues), 1)

    priorities = {}
    for p in ['Low', 'Medium', 'High', 'Urgent']:
        priorities[p] = Issue.query.filter_by(priority=p).count()

    categories = db.session.query(Issue.category, func.count(Issue.id)).group_by(Issue.category).all()

    return jsonify(format_response({
        'total_filed': total,
        'active': active,
        'resolved': resolved,
        'escalated': escalated,
        'avg_resolution_days': avg_resolution,
        'resolution_rate': round(resolved / total * 100, 1) if total > 0 else 0,
        'priority_distribution': priorities,
        'category_distribution': {c: n for c, n in categories},
    }))


@analytics_bp.route('/api/analytics/departments', methods=['GET'])
def department_analytics():
    departments = Department.query.all()
    data = []
    for dept in departments:
        dept_dict = dept.to_dict()
        total = Issue.query.filter_by(department=dept.name).count()
        resolved = Issue.query.filter_by(department=dept.name, status='Resolved').count()
        dept_dict['live_total'] = total
        dept_dict['live_resolved'] = resolved
        dept_dict['live_resolve_rate'] = round(resolved / total * 100, 1) if total > 0 else 0
        data.append(dept_dict)
    return jsonify(format_response(data))


@analytics_bp.route('/api/analytics/officers', methods=['GET'])
def officer_analytics():
    officers = Officer.query.order_by(Officer.resolved_count.desc()).all()
    return jsonify(format_response([o.to_dict() for o in officers]))


@analytics_bp.route('/api/analytics/ai', methods=['GET'])
def ai_analytics():
    analyses = AIAnalysis.query.all()
    total = len(analyses)
    if total == 0:
        return jsonify(format_response({'total_analyses': 0, 'avg_confidence': 0, 'categories': {}}))

    avg_conf = sum(a.confidence or 0 for a in analyses) / total
    cats = {}
    for a in analyses:
        cats[a.category] = cats.get(a.category, 0) + 1

    return jsonify(format_response({
        'total_analyses': total,
        'avg_confidence': round(avg_conf, 1),
        'category_distribution': cats,
    }))


@analytics_bp.route('/api/analytics/trends', methods=['GET'])
def trends():
    period = request.args.get('period', 'weekly')
    now = datetime.utcnow()

    if period == 'daily':
        days = 7
        delta = timedelta(days=1)
    elif period == 'monthly':
        days = 90
        delta = timedelta(days=30)
    else:
        days = 28
        delta = timedelta(days=7)

    data = []
    cursor = now - timedelta(days=days)
    while cursor < now:
        end = cursor + delta
        count = Issue.query.filter(Issue.created_at >= cursor, Issue.created_at < end).count()
        resolved = Issue.query.filter(Issue.created_at >= cursor, Issue.created_at < end, Issue.status == 'Resolved').count()
        data.append({'date': cursor.strftime('%Y-%m-%d'), 'filed': count, 'resolved': resolved})
        cursor = end

    return jsonify(format_response(data))
