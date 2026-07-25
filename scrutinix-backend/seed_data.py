"""
seed_data.py — Database Seeder for Scrutinix

Creates demo users and sample reports so the app looks alive on first run.
Run with: python seed_data.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models.user import User
from models.report import Report, Vote, Comment
import bcrypt
from datetime import datetime, timedelta, timezone
import random


def hash_pw(pw):
    return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def seed():
    app = create_app()

    with app.app_context():
        # Check if data already exists
        if User.query.count() > 0:
            print('[SKIP] Database already has data. Clear scrutinix.db and try again.')
            return

        print('[SEEDING] Creating demo users...')

        # ── Create Demo Users ────────────────────────────
        users = []
        user_data = [
            ('aditya_kumar', 'Aditya Kumar', '9876543210'),
            ('priya_sharma', 'Priya Sharma', '8765432109'),
            ('rahul_verma', 'Rahul Verma', '7654321098'),
            ('neha_gupta', 'Neha Gupta', '6543210987'),
            ('vikram_singh', 'Vikram Singh', '5432109876'),
        ]

        for uname, nickname, phone in user_data:
            u = User(
                username=uname,
                nickname=nickname,
                phone_number=phone,
                phone_verified=True,
                password_hash=hash_pw('password123'),
            )
            db.session.add(u)
            users.append(u)

        db.session.commit()
        print(f'  [OK] Created {len(users)} demo users')

        # ── Create Sample Reports ────────────────────────
        print('[SEEDING] Creating sample reports...')
        reports = []

        report_data = [
            {
                'user': 0,
                'type': 'sms',
                'phone': '9988776655',
                'category': 'job_fraud',
                'desc': 'Received SMS from this number offering work-from-home job with guaranteed ₹50,000/month income. Asked to pay ₹2,000 registration fee. Classic advance-fee fraud pattern. The message contained multiple red flags including unrealistic promises and payment demands.',
                'job_desc': 'Earn ₹50,000 per month from home! No experience required. Simple copy-paste work. Registration fee ₹2,000 only. WhatsApp us for details. Guaranteed income. Limited seats available. Apply now!',
                'days_ago': 2,
            },
            {
                'user': 1,
                'type': 'whatsapp',
                'phone': '9988776655',
                'category': 'job_fraud',
                'desc': 'Same number sent WhatsApp messages to multiple people in our college group. Claims to be HR from a fake company called "TechVision Solutions". URL leads to a phishing page collecting personal data.',
                'days_ago': 4,
            },
            {
                'user': 2,
                'type': 'sms',
                'phone': '9988776655',
                'category': 'phishing',
                'desc': 'This number also sends links that look like bank verification pages. After investigating, the domain was registered just 3 days ago. Clearly a phishing operation running job fraud and financial scams simultaneously.',
                'days_ago': 6,
            },
            {
                'user': 3,
                'type': 'email',
                'email': 'hr@techindia-careers.com',
                'category': 'job_fraud',
                'desc': 'Received job offer from this email for "Data Entry Specialist" role. Company website looks professional but has no verifiable information. They asked for Aadhaar and PAN card scans during the first email itself, which is a huge red flag.',
                'job_desc': 'Data Entry Specialist - Remote Position. Salary: ₹40,000-60,000/month. No experience needed. Immediate joining. Please share your Aadhaar and PAN for processing. Interview via WhatsApp only.',
                'days_ago': 3,
            },
            {
                'user': 4,
                'type': 'email',
                'email': 'hr@techindia-careers.com',
                'category': 'job_fraud',
                'desc': 'Same email contacted me for a "Customer Service Representative" position. When I asked for company registration details, they stopped responding. The job posting was on multiple platforms with slightly different descriptions.',
                'job_desc': 'Hiring Customer Service Representative. Work from mobile! Earn daily ₹1,000-2,000. Commission based. Be your own boss. Flexible hours. Contact immediately as limited seats available!',
                'days_ago': 5,
            },
            {
                'user': 0,
                'type': 'email',
                'email': 'hr@techindia-careers.com',
                'category': 'phishing',
                'desc': 'Third report on this email. They sent a "joining letter" PDF that contains a macro virus. Antivirus caught it. This operation is collecting identity documents and distributing malware.',
                'days_ago': 1,
            },
            {
                'user': 1,
                'type': 'sms',
                'phone': '8877665544',
                'category': 'spam',
                'desc': 'Constant spam messages about cryptocurrency investment opportunities. At least 5-6 messages per day. Number appears to be spoofed as it changes slightly each time but the content is identical.',
                'days_ago': 7,
            },
            {
                'user': 2,
                'type': 'whatsapp',
                'phone': '7766554433',
                'category': 'harassment',
                'desc': 'After rejecting a job offer from this number, the person started sending threatening messages. They threatened to share my personal information that I had provided during the interview process.',
                'days_ago': 10,
            },
            {
                'user': 3,
                'type': 'sms',
                'phone': '6655443322',
                'category': 'phishing',
                'desc': 'This number sends SMS with links claiming to be from SBI bank asking to update KYC. The link leads to a fake SBI login page. Multiple people in my area received the same message.',
                'days_ago': 15,
            },
            {
                'user': 4,
                'type': 'sms',
                'phone': '5544332211',
                'category': 'spam',
                'desc': 'Lottery scam SMS claiming I won ₹10 lakhs. Asks to call another number and pay "processing fee" of ₹5,000. Very common pattern but still catches people off guard.',
                'days_ago': 20,
            },
        ]

        for rd in report_data:
            r = Report(
                user_id=users[rd['user']].id,
                report_type=rd['type'],
                phone_number=rd.get('phone'),
                email_id=rd.get('email'),
                message_description=rd['desc'],
                job_description=rd.get('job_desc'),
                category=rd['category'],
                created_at=datetime.now(timezone.utc) - timedelta(days=rd['days_ago']),
            )
            db.session.add(r)
            reports.append(r)

        db.session.commit()
        print(f'  [OK] Created {len(reports)} sample reports')

        # ── Add Some Votes ───────────────────────────────
        print('[SEEDING] Adding votes...')
        vote_count = 0
        for r in reports[:6]:  # Add votes to first 6 reports
            for u in users:
                if u.id != r.user_id and random.random() > 0.3:
                    vote_type = 'up' if random.random() > 0.15 else 'down'
                    v = Vote(report_id=r.id, user_id=u.id, vote_type=vote_type)
                    db.session.add(v)
                    if vote_type == 'up':
                        r.upvotes += 1
                    else:
                        r.downvotes += 1
                    vote_count += 1

        db.session.commit()
        print(f'  [OK] Added {vote_count} votes')

        # ── Add Some Comments ────────────────────────────
        print('[SEEDING] Adding comments...')
        sample_comments = [
            'I received the same message! Definitely a scam.',
            'Reported to the cyber cell. Thanks for flagging this.',
            'This number has been active for months. Good to see it documented.',
            'Be careful everyone, these scammers are getting more sophisticated.',
            'The same email tried to contact our HR department too.',
        ]

        comment_count = 0
        for i, r in enumerate(reports[:5]):
            for j, text in enumerate(sample_comments[:3]):
                c = Comment(
                    report_id=r.id,
                    user_id=users[(i + j + 1) % len(users)].id,
                    content=text,
                    created_at=r.created_at + timedelta(hours=random.randint(1, 48)),
                )
                db.session.add(c)
                comment_count += 1

        db.session.commit()
        print(f'  [OK] Added {comment_count} comments')

        print('\n[DONE] Database seeded successfully!')
        print('')
        print('  Demo Login Credentials:')
        print('  -----------------------------------------')
        print('  Username: aditya_kumar   Password: password123')
        print('  Username: priya_sharma   Password: password123')
        print('  Username: rahul_verma    Password: password123')
        print('  Phone:    9876543210     Password: password123')
        print('  -----------------------------------------')
        print('')


if __name__ == '__main__':
    seed()
