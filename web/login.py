from flask_login import LoginManager


login = LoginManager()
login.login_view = "auth.login_page"


@login.user_loader
def user_loader(user_id: int):
    return None
