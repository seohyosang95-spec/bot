from flask import Blueprint, render_template

page_bp = Blueprint('page', __name__)

@page_bp.route('/')
def index():
    return render_template('index.html')

@page_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@page_bp.route('/public-posts')
def public_posts():
    return render_template('public_posts.html')

@page_bp.route('/public-posts/<int:uc_seq>')
def public_detail(uc_seq):
    return render_template('public_detail.html')