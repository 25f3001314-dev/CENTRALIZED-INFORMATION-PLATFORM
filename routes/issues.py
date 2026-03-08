import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from models import db
from models.issue import Issue
from models.timeline import Timeline
from models.rating import Rating
from models.escalation import EscalationLog
from services import ai_service, blockchain_service, assignment_service, integration_service
from utils.helpers import generate_issue_id, format_response

issues_bp = Blueprint('issues', __name__)
logger = logging.getLogger(__name__)


@issues_bp.route('/api/issues', methods=['GET'])
def list_issues():
    query = Issue.query
    status = request.args.get('status')
    category = request.args.get('category')
    department = request.args.get('department')
    priority = request.args.get('priority')
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    if department:
        query = query.filter_by(department=department)
    if priority:
        query = query.filter_by(priority=priority)
    issues = query.order_by(Issue.created_at.desc()).all()
    return jsonify(format_response([i.to_dict() for i in issues]))


@issues_bp.route('/api/issues', methods=['POST'])
def create_issue():
    data = request.get_json()
    if not data:
        return jsonify(format_response(message='No data provided', status=400)), 400

    issue_id = generate_issue_id()
    text = f"{data.get('title', '')} {data.get('description', '')}"

    category, confidence = ai_service.categorize_issue(text)
    priority, score = ai_service.calculate_priority(text, category)
    suggested_dept = ai_service.get_suggested_dept(category)

    final_category = data.get('category') or category
    final_dept = data.get('department') or suggested_dept
    final_priority = data.get('priority') or priority

    issue = Issue(
        id=issue_id,
        title=data.get('title', 'Untitled'),
        description=data.get('description', ''),
        category=final_category,
        department=final_dept,
        priority=final_priority,
        status='Filed',
        progress=0,
        lat=data.get('lat'),
        lng=data.get('lng'),
        location=data.get('location', ''),
        citizen_name=data.get('citizen_name', ''),
        citizen_phone=data.get('citizen_phone', ''),
        citizen_email=data.get('citizen_email', ''),
        photos='{}',
    )

    officer_name, officer_id = assignment_service.assign_officer(issue)
    if officer_name:
        issue.officer = officer_name
        issue.officer_id = officer_id

    db.session.add(issue)
    db.session.flush()

    tl = Timeline(issue_id=issue.id, step_name='Issue Filed',
                  description=f'Complaint registered by {issue.citizen_name}', status='done')
    db.session.add(tl)

    if officer_name:
        tl2 = Timeline(issue_id=issue.id, step_name='Assigned to Officer',
                       description=f'Issue assigned to {officer_name}', status='current')
        db.session.add(tl2)

    db.session.commit()

    try:
        blockchain_service.add_block(issue.id, 'Issue Created', {
            'title': issue.title, 'category': final_category, 'priority': final_priority
        })
    except Exception as e:
        logger.warning("Blockchain error: %s", e)

    if issue.citizen_phone:
        integration_service.send_sms(issue.citizen_phone,
            f"Your complaint {issue.id} has been registered. Category: {final_category}. We will update you shortly.",
            issue.id)
    integration_service.sync_to_cpgrams(issue)

    return jsonify(format_response(issue.to_dict(), 'Issue created successfully')), 201


@issues_bp.route('/api/issues/<issue_id>', methods=['GET'])
def get_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    data = issue.to_dict()
    timelines = Timeline.query.filter_by(issue_id=issue_id).order_by(Timeline.timestamp).all()
    data['timeline'] = [t.to_dict() for t in timelines]
    from models.ai_analysis import AIAnalysis
    ai = AIAnalysis.query.filter_by(issue_id=issue_id).first()
    data['ai_analysis'] = ai.to_dict() if ai else None
    chain = blockchain_service.get_chain_for_issue(issue_id)
    data['blockchain'] = chain
    return jsonify(format_response(data))


@issues_bp.route('/api/issues/<issue_id>', methods=['PUT'])
def update_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    data = request.get_json()
    old_status = issue.status

    for field in ['title', 'description', 'status', 'progress', 'priority', 'officer', 'department']:
        if field in data:
            setattr(issue, field, data[field])
    issue.updated_at = datetime.utcnow()
    db.session.commit()

    if 'status' in data and data['status'] != old_status:
        tl = Timeline(issue_id=issue.id, step_name=f"Status: {data['status']}",
                      description=f"Status changed from {old_status} to {data['status']}", status='done')
        db.session.add(tl)
        db.session.commit()
        try:
            blockchain_service.add_block(issue.id, 'Status Updated', {
                'old_status': old_status, 'new_status': data['status']
            })
        except Exception as e:
            logger.warning("Blockchain error: %s", e)
        if issue.citizen_phone:
            integration_service.send_sms(issue.citizen_phone,
                f"Issue {issue.id} status updated: {data['status']}", issue.id)

    return jsonify(format_response(issue.to_dict()))


@issues_bp.route('/api/issues/<issue_id>/escalate', methods=['POST'])
def escalate_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    data = request.get_json() or {}
    issue.escalated = True
    issue.priority = 'Urgent'
    issue.status = 'Escalated'
    issue.updated_at = datetime.utcnow()
    log = EscalationLog(
        issue_id=issue.id,
        reason=data.get('reason', 'Manual escalation'),
        escalated_to=data.get('escalated_to', 'Senior Nodal Officer'),
    )
    db.session.add(log)
    db.session.commit()
    try:
        blockchain_service.add_block(issue.id, 'Escalated', {'reason': log.reason})
    except Exception as e:
        logger.warning("Blockchain error: %s", e)
    if issue.citizen_phone:
        integration_service.send_sms(issue.citizen_phone,
            f"Issue {issue.id} has been escalated to senior officer for urgent resolution.", issue.id)
    return jsonify(format_response(issue.to_dict(), 'Issue escalated'))


@issues_bp.route('/api/issues/<issue_id>/rate', methods=['POST'])
def rate_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    data = request.get_json()
    if not data or 'stars' not in data:
        return jsonify(format_response(message='stars required', status=400)), 400
    rating = Rating(issue_id=issue_id, stars=data['stars'], feedback=data.get('feedback', ''))
    db.session.add(rating)
    db.session.commit()
    return jsonify(format_response(rating.to_dict(), 'Rating submitted'))


@issues_bp.route('/api/issues/<issue_id>/blockchain', methods=['GET'])
def get_blockchain(issue_id):
    chain = blockchain_service.get_chain_for_issue(issue_id)
    valid, msg = blockchain_service.validate_chain(issue_id)
    return jsonify(format_response({'chain': chain, 'valid': valid, 'message': msg}))
