import os
from flask import Flask
from flask_login import LoginManager, UserMixin, login_user, logout_user
from apps.student import app as student_app
from apps.llm import app as llm_app
from apps.social import app as social_app
from apps.admin import app as admin_app 
from apps.common import app as common_app
from apps.user import app as user_app
from apps.imageUploadSolve import app as imageUploadSolve_app
from apps.statistics import app as statistics_app
from flask_cors import CORS

app = Flask(__name__)

# 注册带/api前缀的blueprint（保持向后兼容）
app.register_blueprint(student_app, url_prefix='/api')
app.register_blueprint(llm_app, url_prefix='/api')
app.register_blueprint(social_app, url_prefix='/api')
app.register_blueprint(admin_app, url_prefix='/api')
app.register_blueprint(statistics_app, url_prefix='/api')
app.register_blueprint(user_app, url_prefix='/api')
app.register_blueprint(common_app, url_prefix='/api')
app.register_blueprint(imageUploadSolve_app, url_prefix='/api')

# 注册不带前缀的blueprint（新的API调用方式），使用唯一名称避免冲突
app.register_blueprint(admin_app, name='admin_no_prefix')
app.register_blueprint(statistics_app, name='statistics_no_prefix')
app.register_blueprint(common_app, name='common_no_prefix')

CORS(app)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'change-me')

# 安全模块
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index' 
login_manager.login_message = "先登录哈"

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    return User(id=user_id,username=user_id,password_hash="11111111")

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
