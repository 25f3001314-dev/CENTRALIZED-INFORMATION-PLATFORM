import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from models import db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    CORS(app)

    from routes.issues import issues_bp
    from routes.photos import photos_bp
    from routes.analytics import analytics_bp
    from routes.departments import departments_bp

    app.register_blueprint(issues_bp)
    app.register_blueprint(photos_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(departments_bp)

    from services.integration_service import parse_whatsapp_webhook

    @app.route('/api/webhook/whatsapp', methods=['POST'])
    def whatsapp_webhook():
        payload = request.get_json() or {}
        issue_data = parse_whatsapp_webhook(payload)
        if not issue_data:
            return jsonify({'error': 'Invalid payload'}), 400
        from models.issue import Issue
        from utils.helpers import generate_issue_id
        from services import ai_service, assignment_service
        text = f"{issue_data['title']} {issue_data['description']}"
        category, conf = ai_service.categorize_issue(text)
        priority, score = ai_service.calculate_priority(text, category)
        issue = Issue(
            id=generate_issue_id(),
            title=issue_data['title'],
            description=issue_data['description'],
            category=category,
            department=ai_service.get_suggested_dept(category),
            priority=priority,
            status='Filed',
            progress=0,
            citizen_phone=issue_data.get('citizen_phone', ''),
            photos='{}',
        )
        officer_name, officer_id = assignment_service.assign_officer(issue)
        if officer_name:
            issue.officer = officer_name
            issue.officer_id = officer_id
        db.session.add(issue)
        db.session.commit()
        return jsonify({'status': 'success', 'issue_id': issue.id}), 201

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'ok',
            'service': 'CivicPulse API',
            'version': '1.0.0',
            'database': 'connected'
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'status': 'error', 'message': 'Resource not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

    with app.app_context():
        # Import all models so SQLAlchemy registers their tables before create_all
        from models import issue, officer, department, timeline, rating, blockchain, ai_analysis, escalation  # noqa: F401
        db.create_all()
        from utils.seed_data import seed_database
        seed_database(app)

    from services.escalation_service import start_scheduler
    start_scheduler(app)

    return app


if __name__ == '__main__':
    app = create_app()
    logger.info("Starting CivicPulse API server...")
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
