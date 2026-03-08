import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def seed_database(app):
    """Seed the database with initial data on first run."""
    with app.app_context():
        from models import db
        from models.department import Department
        from models.officer import Officer
        from models.issue import Issue
        from models.timeline import Timeline
        from models.ai_analysis import AIAnalysis
        from services.blockchain_service import add_block

        if Issue.query.count() > 0:
            logger.info("Database already seeded, skipping")
            return

        logger.info("Seeding database...")

        departments = [
            Department(name='Public Works Department', description='Road & infrastructure maintenance',
                       officer_in_charge='Rajesh Kumar', total_issues=42, resolve_rate=78.5, avg_days=4.2),
            Department(name='Water Supply & Sewerage Board', description='Water supply and drainage',
                       officer_in_charge='Priya Singh', total_issues=28, resolve_rate=85.7, avg_days=2.8),
            Department(name='Municipal Solid Waste Management', description='Garbage collection and sanitation',
                       officer_in_charge='Arun Verma', total_issues=35, resolve_rate=91.4, avg_days=1.5),
            Department(name='Electricity Department', description='Street lights and power supply',
                       officer_in_charge='Suresh Nair', total_issues=19, resolve_rate=94.7, avg_days=1.8),
            Department(name='Parks & Recreation Department', description='Park maintenance and green spaces',
                       officer_in_charge='Meena Rao', total_issues=12, resolve_rate=66.7, avg_days=8.1),
            Department(name='Urban Development Authority', description='Building and infrastructure approval',
                       officer_in_charge='Vikram Sharma', total_issues=8, resolve_rate=75.0, avg_days=12.3),
        ]
        for d in departments:
            db.session.add(d)
        db.session.flush()

        officers = [
            Officer(name='Rajesh Kumar', department='Public Works Department', badge_number='PWD-001',
                    active_cases=3, resolved_count=28, avg_rating=4.2, gps_lat=12.9716, gps_lng=77.5946),
            Officer(name='Priya Singh', department='Water Supply & Sewerage Board', badge_number='WSB-001',
                    active_cases=2, resolved_count=41, avg_rating=4.6, gps_lat=12.9350, gps_lng=77.6244),
            Officer(name='Arun Verma', department='Municipal Solid Waste Management', badge_number='MSW-001',
                    active_cases=5, resolved_count=67, avg_rating=4.4, gps_lat=12.9500, gps_lng=77.5800),
            Officer(name='Suresh Nair', department='Electricity Department', badge_number='ELEC-001',
                    active_cases=1, resolved_count=52, avg_rating=4.8, gps_lat=12.9200, gps_lng=77.6100),
            Officer(name='Meena Rao', department='Parks & Recreation Department', badge_number='PARK-001',
                    active_cases=2, resolved_count=18, avg_rating=3.9, gps_lat=12.9600, gps_lng=77.5700),
            Officer(name='Vikram Sharma', department='Urban Development Authority', badge_number='UDA-001',
                    active_cases=1, resolved_count=14, avg_rating=4.1, gps_lat=12.9800, gps_lng=77.5500),
        ]
        for o in officers:
            db.session.add(o)
        db.session.flush()

        now = datetime.utcnow()
        issues_data = [
            {
                'id': 'CP-2024-78341',
                'title': 'Pothole on MG Road causing accidents',
                'description': 'There is a large pothole near Residency Road junction, MG Road that has caused 3 vehicle accidents this week. Requires immediate repair.',
                'category': 'Roads',
                'department': 'Public Works Department',
                'officer': 'Rajesh Kumar',
                'priority': 'High',
                'status': 'In Progress',
                'progress': 60,
                'lat': 12.9716,
                'lng': 77.5946,
                'location': 'MG Road, Residency Junction, Bengaluru',
                'citizen_name': 'Aarav Sharma',
                'citizen_phone': '9876543210',
                'citizen_email': 'aarav@example.com',
                'created_at': now - timedelta(days=3),
                'escalated': False,
            },
            {
                'id': 'CP-2024-78342',
                'title': 'Garbage overflow at Koramangala market',
                'description': 'The garbage bins at Koramangala 4th Block market have been overflowing for 5 days. Serious health hazard for residents and shopkeepers.',
                'category': 'Sanitation',
                'department': 'Municipal Solid Waste Management',
                'officer': 'Arun Verma',
                'priority': 'Urgent',
                'status': 'Escalated',
                'progress': 30,
                'lat': 12.9352,
                'lng': 77.6245,
                'location': 'Koramangala 4th Block, Bengaluru',
                'citizen_name': 'Divya Krishnan',
                'citizen_phone': '9876543211',
                'citizen_email': 'divya@example.com',
                'created_at': now - timedelta(days=6),
                'escalated': True,
            },
            {
                'id': 'CP-2024-78343',
                'title': 'Street lights not working — Indiranagar',
                'description': 'The street lights on 100 Feet Road, Indiranagar have not been working for 2 weeks. The area is completely dark at night, posing safety risks.',
                'category': 'Electrical',
                'department': 'Electricity Department',
                'officer': 'Suresh Nair',
                'priority': 'High',
                'status': 'Assigned',
                'progress': 20,
                'lat': 12.9784,
                'lng': 77.6408,
                'location': '100 Feet Road, Indiranagar, Bengaluru',
                'citizen_name': 'Karthik Reddy',
                'citizen_phone': '9876543212',
                'citizen_email': 'karthik@example.com',
                'created_at': now - timedelta(days=14),
                'escalated': True,
            },
            {
                'id': 'CP-2024-78344',
                'title': 'Water pipeline burst — Jayanagar',
                'description': 'A major water pipeline has burst near Jayanagar 4th Block causing flooding on the road and water wastage. Immediate repair needed.',
                'category': 'Water',
                'department': 'Water Supply & Sewerage Board',
                'officer': 'Priya Singh',
                'priority': 'Urgent',
                'status': 'In Progress',
                'progress': 75,
                'lat': 12.9250,
                'lng': 77.5938,
                'location': 'Jayanagar 4th Block, Bengaluru',
                'citizen_name': 'Sneha Patel',
                'citizen_phone': '9876543213',
                'citizen_email': 'sneha@example.com',
                'created_at': now - timedelta(hours=18),
                'escalated': False,
            },
            {
                'id': 'CP-2024-78345',
                'title': 'Park benches damaged — Cubbon Park',
                'description': 'Multiple park benches in Cubbon Park near the main entrance are damaged and have sharp metal edges. Children getting hurt. Needs replacement.',
                'category': 'Parks',
                'department': 'Parks & Recreation Department',
                'officer': 'Meena Rao',
                'priority': 'Medium',
                'status': 'Resolved',
                'progress': 100,
                'lat': 12.9763,
                'lng': 77.5929,
                'location': 'Cubbon Park, Main Entrance, Bengaluru',
                'citizen_name': 'Rahul Menon',
                'citizen_phone': '9876543214',
                'citizen_email': 'rahul@example.com',
                'created_at': now - timedelta(days=10),
                'escalated': False,
            },
        ]

        for idata in issues_data:
            issue = Issue(
                id=idata['id'],
                title=idata['title'],
                description=idata['description'],
                category=idata['category'],
                department=idata['department'],
                officer=idata['officer'],
                priority=idata['priority'],
                status=idata['status'],
                progress=idata['progress'],
                lat=idata['lat'],
                lng=idata['lng'],
                location=idata['location'],
                citizen_name=idata['citizen_name'],
                citizen_phone=idata['citizen_phone'],
                citizen_email=idata['citizen_email'],
                created_at=idata['created_at'],
                updated_at=idata['created_at'],
                escalated=idata['escalated'],
                photos='{}',
            )
            db.session.add(issue)
            db.session.flush()

            _create_timeline(issue, db)

            ai = AIAnalysis(
                issue_id=issue.id,
                category=issue.category,
                subcategory=issue.title[:50],
                confidence=87.5,
                severity='High' if issue.priority in ['High', 'Urgent'] else 'Medium',
                suggested_dept=issue.department,
                est_resolution='3-5 days',
            )
            db.session.add(ai)

        db.session.commit()

        for idata in issues_data:
            try:
                add_block(idata['id'], 'Issue Created', {'title': idata['title'], 'status': 'Filed'})
                if idata['status'] not in ['Filed']:
                    add_block(idata['id'], 'Status Updated', {'status': idata['status'], 'officer': idata['officer']})
            except Exception as e:
                logger.warning("Could not add blockchain block for %s: %s", idata['id'], e)

        logger.info("Database seeded successfully with %d issues", len(issues_data))
        print("✅ Database seeded with sample data")


def _create_timeline(issue, db):
    from models.timeline import Timeline

    statuses = ['Filed', 'Assigned', 'In Progress', 'Resolved']
    current_idx = statuses.index(issue.status) if issue.status in statuses else 0

    steps = [
        ('Issue Filed', f'Complaint registered by {issue.citizen_name}'),
        ('Assigned to Officer', f'Issue assigned to {issue.officer}'),
        ('Field Inspection', 'Officer conducting site visit and assessment'),
        ('Work in Progress', 'Repair/remediation work underway'),
        ('Resolved', 'Issue resolved and verified'),
    ]

    for i, (step, desc) in enumerate(steps):
        if i <= current_idx:
            status = 'done'
        elif i == current_idx + 1:
            status = 'current'
        else:
            status = 'pending'

        tl = Timeline(
            issue_id=issue.id,
            step_name=step,
            description=desc,
            status=status,
            timestamp=issue.created_at + timedelta(hours=i*6) if status == 'done' else datetime.utcnow()
        )
        db.session.add(tl)
