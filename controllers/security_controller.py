import os
from functools import wraps
from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import generate_password_hash
from extensions import db
from models import Post, SecurityEvent, User

security_bp = Blueprint('security', __name__, url_prefix='/api/security')

def require_api_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        expected = current_app.config.get('SECURITY_API_KEY', '')
        if not expected or request.headers.get('X-API-Key', '') != expected:
            return jsonify({'msg': 'API 키가 없거나 잘못되었습니다.'}), 401
        return fn(*args, **kwargs)
    return wrapper

def _create_security_post(ev):
    bot = User.query.filter_by(username='soarbot').first()
    if not bot:
        bot = User(username='soarbot', password=generate_password_hash(os.urandom(16).hex()))
        db.session.add(bot)
        db.session.flush()

    post = Post(
        title=f'[보안][{ev.student}] {ev.src_ip} 접근 거부 ({ev.severity})',
        content=f'{ev.reason}\n시도 계정: {ev.users}\n마지막 시도: {ev.last_seen}\n수집: {ev.generated_at}',
        category='보안', author_id=bot.id
    )
    db.session.add(post)
    db.session.flush()
    return post.id

@security_bp.route('/events', methods=['POST'])
@require_api_key
def create_security_event():
    data = request.get_json(silent=True) or {}
    student = (data.get('student') or '').strip()
    src_ip = data.get('src_ip')
    decision = data.get('decision')
    if not student or not src_ip or decision not in ('allow', 'deny'):
        return jsonify({'msg': 'student, src_ip, decision(allow|deny) 은 필수입니다.'}), 400

    ev = SecurityEvent(
        student=student[:50], src_ip=src_ip,
        fail_count=int(data.get('fail_count') or 0), decision=decision,
        severity=data.get('severity', 'Low'), reason=data.get('reason'),
        users=data.get('users'), last_seen=data.get('last_seen'),
        window_min=data.get('window_min'),
        source=data.get('source', 'login_guard'),
        generated_at=data.get('generated_at'),
    )
    db.session.add(ev)
    db.session.flush()

    post_id = None
    if decision == 'deny' and current_app.config.get('AUTO_POST_ON_DENY'):
        post_id = _create_security_post(ev)

    db.session.commit()
    return jsonify({'id': ev.id, 'student': ev.student, 'decision': ev.decision, 'post_id': post_id}), 201

@security_bp.route('/events', methods=['GET'])
def list_security_events():
    student = request.args.get('student')
    decision = request.args.get('decision')
    limit = request.args.get('limit', default=20, type=int)

    query = SecurityEvent.query
    if student:
        query = query.filter_by(student=student)
    if decision in ('allow', 'deny'):
        query = query.filter_by(decision=decision)

    rows = query.order_by(SecurityEvent.id.desc()).limit(min(limit, 100)).all()
    return jsonify({'count': len(rows), 'events': [r.to_dict() for r in rows]})

@security_bp.route('/events/summary', methods=['GET'])
def security_events_summary():
    from sqlalchemy import func
    student = request.args.get('student')
    q1 = db.session.query(SecurityEvent.decision, func.count(SecurityEvent.id))
    q2 = db.session.query(SecurityEvent.src_ip, func.sum(SecurityEvent.fail_count)).filter(SecurityEvent.decision == 'deny')
    if student:
        q1 = q1.filter(SecurityEvent.student == student)
        q2 = q2.filter(SecurityEvent.student == student)

    by_decision = dict(q1.group_by(SecurityEvent.decision).all())
    top = q2.group_by(SecurityEvent.src_ip).order_by(func.sum(SecurityEvent.fail_count).desc()).limit(5).all()

    return jsonify({
        'student': student,
        'by_decision': by_decision,
        'top_deny_ips': [{'src_ip': ip, 'fails': int(n)} for ip, n in top],
    })

@security_bp.route('/students', methods=['GET'])
def list_students():
    rows = db.session.query(SecurityEvent.student).distinct().order_by(SecurityEvent.student).all()
    return jsonify({'students': [r[0] for r in rows]})