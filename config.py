import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://<user>:<password>@localhost:3306/my_new_board_db',
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-only-change-me')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    SECURITY_API_KEY = os.environ.get('SECURITY_API_KEY', '')
    AUTO_POST_ON_DENY = os.environ.get('AUTO_POST_ON_DENY', '0') == '1'

    PUBLIC_API_KEY = os.environ.get('PUBLIC_API_KEY')
    PUBLIC_API_URL = 'http://apis.data.go.kr/6260000/RecommendedService/getRecommendedKr'