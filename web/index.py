from flask import Blueprint, render_template
from flask_login import login_required
from .logger import Logger


index = Blueprint("base", __name__)


@index.route("/")
@login_required
def index_page():
    Logger.print_load_page_log("index")
    return render_template("index/index.html")
