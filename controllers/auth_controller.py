from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from extensions import db
from models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    if not username or not password:
        return jsonify({'msg': '아이디와 비밀번호는 필수입니다.'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'msg': '이미 존재하는 아이디입니다.'}), 400

    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': '회원가입 성공', 'username': user.username}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'msg': '아이디 또는 비밀번호가 올바르지 않습니다.'}), 401

    access_token = create_access_token(identity=user.username)
    return jsonify({'access_token': access_token, 'username': user.username}), 200