from flask import render_template

from . import main_bp
current_user = None
@main_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('base.html', current_user=current_user)


@main_bp.route('/', methods=['GET', 'POST'])
def about():
    return render_template('base.html', current_user=current_user)


