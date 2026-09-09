from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Post, User

post_bp = Blueprint('post', __name__, url_prefix='/api')

@post_bp.route('/posts', methods=['GET'])
def get_posts():
    limit = request.args.get('limit', default=5, type=int)
    cursor = request.args.get('cursor', default=None, type=int)
    search = request.args.get('search', default='', type=str)
    category = request.args.get('category', default='전체', type=str)

    query = Post.query
    if category and category != '전체':
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Post.title.like(f'%{search}%') | Post.content.like(f'%{search}%'))
    if cursor:
        query = query.filter(Post.id < cursor)

    posts = query.order_by(Post.id.desc()).limit(limit + 1).all()
    has_more = len(posts) > limit
    if has_more:
        posts = posts[:limit]
    next_cursor = posts[-1].id if (has_more and posts) else None

    return jsonify({'posts': [p.to_dict() for p in posts], 'has_more': has_more, 'next_cursor': next_cursor})

@post_bp.route('/posts', methods=['POST'])
@jwt_required()
def create_post():
    current_user_name = get_jwt_identity()
    user = User.query.filter_by(username=current_user_name).first()
    data = request.get_json(silent=True) or {}
    title = data.get('title')
    content = data.get('content')
    category = data.get('category', '일반')
    if not title or not content:
        return jsonify({'msg': '제목과 내용은 필수입니다.'}), 400

    post = Post(title=title, content=content, category=category, author_id=user.id)
    db.session.add(post)
    db.session.commit()
    return jsonify({'msg': '작성 완료', 'id': post.id}), 201

@post_bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    current_user_name = get_jwt_identity()
    post = Post.query.get_or_404(post_id)
    if post.author.username != current_user_name:
        return jsonify({'msg': '수정 권한이 없습니다.'}), 403

    data = request.get_json(silent=True) or {}
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    post.category = data.get('category', post.category)
    db.session.commit()
    return jsonify({'msg': '수정 완료'})

@post_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    current_user_name = get_jwt_identity()
    post = Post.query.get_or_404(post_id)
    if post.author.username != current_user_name:
        return jsonify({'msg': '삭제 권한이 없습니다.'}), 403

    db.session.delete(post)
    db.session.commit()
    return jsonify({'msg': '삭제 완료'})