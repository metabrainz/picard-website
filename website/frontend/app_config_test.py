from website.frontend import _env_flag, create_app


def test_debug_off_by_default():
    # default_config.py sets DEBUG = False; no override, no env var.
    app = create_app(config_overrides={'TESTING': True})
    assert app.debug is False


def test_debug_on_via_config_override():
    app = create_app(config_overrides={'TESTING': True, 'DEBUG': True})
    assert app.debug is True


def test_debug_env_var_takes_precedence_on(monkeypatch):
    # Env var overrides even a config value of False.
    monkeypatch.setenv('PICARD_WEBSITE_DEBUG', '1')
    app = create_app(config_overrides={'TESTING': True, 'DEBUG': False})
    assert app.debug is True


def test_debug_env_var_takes_precedence_off(monkeypatch):
    monkeypatch.setenv('PICARD_WEBSITE_DEBUG', 'false')
    app = create_app(config_overrides={'TESTING': True, 'DEBUG': True})
    assert app.debug is False


def test_env_flag_recognised_values(monkeypatch):
    for truthy in ('1', 'true', 'TRUE', 'Yes', 'on'):
        monkeypatch.setenv('PICARD_WEBSITE_DEBUG', truthy)
        assert _env_flag('PICARD_WEBSITE_DEBUG') is True
    for falsy in ('0', 'false', 'no', 'off', ''):
        monkeypatch.setenv('PICARD_WEBSITE_DEBUG', falsy)
        assert _env_flag('PICARD_WEBSITE_DEBUG') is False


def test_env_flag_unset_returns_none(monkeypatch):
    monkeypatch.delenv('PICARD_WEBSITE_DEBUG', raising=False)
    assert _env_flag('PICARD_WEBSITE_DEBUG') is None
