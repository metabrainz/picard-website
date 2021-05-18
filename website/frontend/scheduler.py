
from flask_apscheduler import APScheduler

from website.build_plugins import generate_plugins
from website.plugin_utils import load_json_data


def init_scheduler(app):
    logger = app.logger
    config = app.config
    scheduler = APScheduler()
    scheduler.init_app(app)

    @scheduler.task('interval', id='plugins_generate', seconds=config['PLUGINS_REFRESH_INTERVAL_SECONDS'])
    def plugins_generate():
        versions = [z['title'] for z in config['PLUGIN_VERSIONS'].values()]
        build_dir = config['PLUGINS_BUILD_DIR']
        for version in versions:
            logger.info("Generating plugins for version %s in %s", version, build_dir)
            try:
                generate_plugins(build_dir, version)
                # Prefill the cache
                load_json_data(app, version, force_refresh=True)
                logger.info("Plugin generation for version %s successful.", version)
            except Exception as e:
                logger.error("Plugin generation for version %s failed: %s", version, e)


    scheduler.start()
    return scheduler
