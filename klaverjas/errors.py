from flask import render_template, request
from klaverjas import app, db


@app.errorhandler(403)
def forbidden_error(error):
    app.logger.error('403 for {}'.format(request.url))
    return render_template('403.html'), 403


@app.errorhandler(404)
def not_found_error(error):
    app.logger.error('404 for {}'.format(request.url))
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.error('500 for {}'.format(request.url))
    db.session.rollback()
    return render_template('500.html'), 500
