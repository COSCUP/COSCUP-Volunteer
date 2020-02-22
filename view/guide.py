from flask import Blueprint
from flask import render_template

VIEW_GUIDE = Blueprint('guide', __name__, url_prefix='/guide')


@VIEW_GUIDE.route('/')
def index():
    return render_template('./guide_index.html')
