from flask import Blueprint
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

VIEW_GUIDE = Blueprint('guide', __name__, url_prefix='/guide')

@VIEW_GUIDE.route('/')
def index():
    return render_template('./guide_index.html')
