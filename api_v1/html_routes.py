from flask import render_template
from api_v1 import bp


@bp.route('/append_book')
def html_routes_append_book():
    print("hello")
    return render_template("test_add_book.html")