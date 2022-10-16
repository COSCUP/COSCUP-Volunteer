''' Guide '''
from flask import Blueprint, render_template

VIEW_GUIDE = Blueprint('guide', __name__, url_prefix='/guide')


@VIEW_GUIDE.route('/')
def index() -> str:
    ''' Index page '''
    return render_template('./guide_index.html')
