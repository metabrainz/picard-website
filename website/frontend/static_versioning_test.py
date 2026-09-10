import os

from flask import url_for

from website.frontend import create_app


def _app():
    app = create_app(config_overrides={'TESTING': True, 'SERVER_NAME': 'localhost'})
    return app


def test_static_url_gets_version_query():
    app = _app()
    # pick a real static file that ships with the app
    rel = 'css/styles.css'
    assert os.path.exists(os.path.join(app.static_folder, rel))
    with app.test_request_context():
        url = url_for('static', filename=rel)
    assert '?v=' in url
    # 8-char hex hash
    version = url.split('?v=')[1]
    assert len(version) == 8
    assert all(c in '0123456789abcdef' for c in version)


def test_static_version_is_stable_for_same_content():
    app = _app()
    with app.test_request_context():
        a = url_for('static', filename='css/styles.css')
        b = url_for('static', filename='css/styles.css')
    assert a == b


def test_static_version_differs_between_different_files():
    app = _app()
    with app.test_request_context():
        a = url_for('static', filename='css/styles.css')
        b = url_for('static', filename='js/jquery.min.js')
    assert a.split('?v=')[1] != b.split('?v=')[1]


def test_missing_static_file_gets_no_version():
    app = _app()
    with app.test_request_context():
        url = url_for('static', filename='does/not/exist.css')
    assert '?v=' not in url


def test_explicit_version_is_not_overridden():
    app = _app()
    with app.test_request_context():
        url = url_for('static', filename='css/styles.css', v='custom')
    assert url.endswith('v=custom')
