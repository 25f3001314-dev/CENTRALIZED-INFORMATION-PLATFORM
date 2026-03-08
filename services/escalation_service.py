import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

SLA_HOURS = {
    'Low': 168,
    'Medium': 120,
    'High': 72,
    'Urgent': 24,
}


def check_and_escalate(app):
    """Check all open issues and escalate if SLA breached."""
    with app.app_context():
        from models.issue import Issue
        from models.escalation import EscalationLog
        from models import db

        now = datetime.utcnow()
        open_issues = Issue.query.filter(Issue.status.notin_(['Resolved', 'Closed'])).all()
        escalated_count = 0

        for issue in open_issues:
            if not issue.created_at:
                continue
            sla_hours = SLA_HOURS.get(issue.priority, 120)
            deadline = issue.created_at + timedelta(hours=sla_hours)

            if now > deadline and not issue.escalated:
                original_priority = issue.priority
                issue.escalated = True
                issue.priority = 'Urgent'
                issue.updated_at = now

                log = EscalationLog(
                    issue_id=issue.id,
                    reason=f"SLA breached: {sla_hours}h exceeded for priority {original_priority}",
                    escalated_to='Senior Nodal Officer',
                    triggered_at=now
                )
                db.session.add(log)
                escalated_count += 1

                logger.info("[ESCALATION] Issue %s escalated to Urgent (SLA %dh breached, was %s)",
                            issue.id, sla_hours, original_priority)
                _send_escalation_notification(issue)

        if escalated_count > 0:
            db.session.commit()
            logger.info("Escalation run complete: %d issues escalated", escalated_count)


def _send_escalation_notification(issue):
    """Log SMS/notification for escalation (mock)."""
    print(f"[SMS ALERT] Issue {issue.id} has been escalated to URGENT priority.")
    print(f"  Citizen: {issue.citizen_name} | Phone: {issue.citizen_phone}")
    print(f"  Title: {issue.title}")
    print(f"  Department: {issue.department}")


def start_scheduler(app):
    """Start the APScheduler background job."""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=check_and_escalate,
            args=[app],
            trigger='interval',
            hours=1,
            id='escalation_check',
            replace_existing=True
        )
        scheduler.start()
        logger.info("Escalation scheduler started (interval: 1 hour)")
        return scheduler
    except ImportError:
        logger.warning("APScheduler not available, escalation scheduler not started")
        return None
