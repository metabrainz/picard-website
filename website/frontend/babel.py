from flask import abort, g, request
from flask_babel import Babel, Locale


def init_app(app):
    with app.app_context():
        babel = Babel(app)
        available_locales = babel.list_translations()
        desired_languages = app.config['SUPPORTED_LANGUAGES']

        found_locales = {}
        for language in desired_languages:
            try:
                locale = Locale.parse(language)
                if locale in available_locales:
                    found_locales[language] = locale.language_name
            except BaseException as e:
                app.logger.error('%s', e)

        if not found_locales:
            found_locales = {str(l): l.language_name for l in available_locales}

        app.config['LANGUAGES'] = found_locales
        app.logger.debug('Languages: %r', list(app.config['LANGUAGES']))

    @app.after_request
    def call_after_request_callbacks(response):
        for callback in getattr(g, 'after_request_callbacks', ()):
            callback(response)
        return response

    def after_this_request(f):
        if not hasattr(g, 'after_request_callbacks'):
            g.after_request_callbacks = []
        g.after_request_callbacks.append(f)
        return f

    def get_locale():
        languages = list(app.config['LANGUAGES'])
        language_arg = request.args.get('l')
        if language_arg is not None:
            if language_arg in languages:

                @after_this_request
                def remember_language(response):
                    response.set_cookie('language', language_arg)

                return language_arg
            else:
                abort(400)
        else:
            language_cookie = request.cookies.get('language')
            if language_cookie is not None:
                if language_cookie in languages:
                    return language_cookie
                else:
                    abort(400)

        return request.accept_languages.best_match(languages)

    @app.context_processor
    def inject_language_var():
        return {
            'active_language': get_locale(),
        }

    babel.init_app(app, locale_selector=get_locale)
