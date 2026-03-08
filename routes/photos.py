import os
import json
import logging
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from models import db
from models.issue import Issue
from models.ai_analysis import AIAnalysis
from services import ai_service, blockchain_service
from utils.helpers import format_response, allowed_file

photos_bp = Blueprint('photos', __name__)
logger = logging.getLogger(__name__)


@photos_bp.route('/api/issues/<issue_id>/photos/before', methods=['POST'])
def upload_before_photo(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    if 'photo' not in request.files:
        return jsonify(format_response(message='No photo in request', status=400)), 400
    file = request.files['photo']
    if file.filename == '':
        return jsonify(format_response(message='Empty filename', status=400)), 400
    if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return jsonify(format_response(message='File type not allowed', status=400)), 400

    filename = secure_filename(f"{issue_id}_before_{file.filename}")
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    meta = ai_service.analyze_photo_metadata(filepath)

    try:
        photos = json.loads(issue.photos or '{}')
    except Exception:
        photos = {}
    photos['before'] = filename
    issue.photos = json.dumps(photos)

    if meta.get('gps'):
        issue.lat = meta['gps']['lat']
        issue.lng = meta['gps']['lng']

    db.session.commit()

    ai = AIAnalysis.query.filter_by(issue_id=issue_id).first()
    if not ai:
        ai = AIAnalysis(issue_id=issue_id)
        db.session.add(ai)
    ai.ocr_text = meta.get('ocr_text', '')
    ai.photo_analysis = json.dumps(meta)
    db.session.commit()

    try:
        blockchain_service.add_block(issue_id, 'Before Photo Uploaded', {'filename': filename, 'gps': meta.get('gps')})
    except Exception as e:
        logger.warning("Blockchain error: %s", e)

    return jsonify(format_response({'filename': filename, 'metadata': meta}, 'Before photo uploaded'))


@photos_bp.route('/api/issues/<issue_id>/photos/after', methods=['POST'])
def upload_after_photo(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    if 'photo' not in request.files:
        return jsonify(format_response(message='No photo in request', status=400)), 400
    file = request.files['photo']
    if file.filename == '':
        return jsonify(format_response(message='Empty filename', status=400)), 400
    if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return jsonify(format_response(message='File type not allowed', status=400)), 400

    filename = secure_filename(f"{issue_id}_after_{file.filename}")
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    comparison = None
    try:
        photos = json.loads(issue.photos or '{}')
    except Exception:
        photos = {}
    photos['after'] = filename
    issue.photos = json.dumps(photos)

    before_filename = photos.get('before')
    if before_filename:
        before_path = os.path.join(current_app.config['UPLOAD_FOLDER'], before_filename)
        if os.path.exists(before_path):
            comparison = ai_service.compare_images(before_path, filepath)
            if comparison.get('verified'):
                issue.status = 'Pending Verification'
                issue.progress = 90

    db.session.commit()

    try:
        blockchain_service.add_block(issue_id, 'After Photo Uploaded', {'filename': filename, 'comparison': comparison})
    except Exception as e:
        logger.warning("Blockchain error: %s", e)

    return jsonify(format_response({'filename': filename, 'comparison': comparison}, 'After photo uploaded'))


@photos_bp.route('/api/issues/<issue_id>/photos/<photo_type>', methods=['GET'])
def get_photo(issue_id, photo_type):
    issue = Issue.query.get_or_404(issue_id)
    try:
        photos = json.loads(issue.photos or '{}')
    except Exception:
        photos = {}
    filename = photos.get(photo_type)
    if not filename:
        return jsonify(format_response(message='Photo not found', status=404)), 404
    upload_dir = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_dir, filename)
