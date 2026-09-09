import requests
from flask import Blueprint, jsonify, current_app

public_bp = Blueprint('public', __name__, url_prefix='/api/public')

@public_bp.route('/posts', methods=['GET'])
def get_public_posts():
    url = current_app.config.get('PUBLIC_API_URL')
    service_key = current_app.config.get('PUBLIC_API_KEY')
    params = {'serviceKey': service_key, 'pageNo': '1', 'numOfRows': '100', 'resultType': 'json'}
    try:
        response = requests.get(url, params=params)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'msg': '공공데이터를 불러오는 중 오류가 발생했습니다.', 'error': str(e)}), 500