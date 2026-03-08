import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def sync_to_cpgrams(issue):
    """Mock CPGRAMS API sync - formats issue as CPGRAMS payload and logs it."""
    payload = {
        'cpgrams_id': f"CPGRAMS-{issue.id}",
        'registration_number': issue.id,
        'subject': issue.title,
        'description': issue.description,
        'category': issue.category,
        'ministry': issue.department,
        'status': _map_status_to_cpgrams(issue.status),
        'priority': issue.priority,
        'citizen_name': issue.citizen_name,
        'citizen_phone': issue.citizen_phone,
        'location': issue.location,
        'filed_at': issue.created_at.isoformat() if issue.created_at else None,
        'sync_at': datetime.utcnow().isoformat(),
    }
    logger.info("[CPGRAMS SYNC] Sending to CPGRAMS API: %s", json.dumps(payload, indent=2))
    print(f"[CPGRAMS] Synced issue {issue.id} to CPGRAMS portal")
    return {'success': True, 'cpgrams_id': payload['cpgrams_id']}


def _map_status_to_cpgrams(status):
    mapping = {
        'Filed': 'PENDING',
        'Assigned': 'UNDER_PROCESS',
        'In Progress': 'UNDER_PROCESS',
        'Escalated': 'ESCALATED',
        'Resolved': 'DISPOSED',
        'Closed': 'CLOSED',
    }
    return mapping.get(status, 'PENDING')


def send_sms(phone, message, issue_id=None):
    """Mock SMS gateway - logs formatted SMS."""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[SMS GATEWAY] [{timestamp}]")
    print(f"  To: {phone}")
    if issue_id:
        print(f"  Issue: {issue_id}")
    print(f"  Message: {message}")
    print(f"  Status: SENT (mock)")
    logger.info("[SMS] Sent to %s: %s", phone, message)
    return {'sent': True, 'to': phone}


def send_whatsapp(phone, message, issue_id=None):
    """Mock WhatsApp Business API notification."""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[WHATSAPP] [{timestamp}]")
    print(f"  To: {phone}")
    if issue_id:
        print(f"  Issue: {issue_id}")
    print(f"  Message: {message}")
    print(f"  Status: SENT (mock)")
    logger.info("[WhatsApp] Sent to %s: %s", phone, message)
    return {'sent': True, 'to': phone}


def parse_whatsapp_webhook(payload):
    """Parse incoming WhatsApp webhook message and extract issue details."""
    try:
        message_text = payload.get('message', {}).get('text', {}).get('body', '')
        sender_phone = payload.get('message', {}).get('from', '')
        lines = message_text.strip().split('\n')
        title = lines[0][:200] if lines else 'WhatsApp Issue'
        description = '\n'.join(lines[1:]) if len(lines) > 1 else message_text
        return {
            'title': title,
            'description': description or title,
            'citizen_phone': sender_phone,
            'source': 'whatsapp',
        }
    except Exception as e:
        logger.error("WhatsApp parse error: %s", e)
        return None
