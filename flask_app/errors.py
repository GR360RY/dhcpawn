from .app import app
from .models import db

from flask import jsonify, render_template, make_response, request

def _define_custom_error_page(code, message=None):
    @app.errorhandler(code)
    def _handler(err):
        print request.path
        if code == 500:
            db.session.rollback()
        if request.path.startswith('/api'):
            response = jsonify(dict({"status":code,"message":message}))
            response.status_code = code
            return response
        return make_response(render_template("errors/{}.html".format(code)), code)

_define_custom_error_page(500,"internal server error")
_define_custom_error_page(404,"page not found")
_define_custom_error_page(403,"forbidden")
