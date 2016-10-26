from __future__ import with_statement
from fabric.api import local
from fabric.colors import green, yellow
from fabric.context_managers import lcd
from fabric.contrib.console import confirm
from fabric.utils import abort
import website.frontend
import os.path


def extract_strings():
    """Extract all strings into messages.pot.

    This command should be run after any translatable strings are updated.
    Otherwise updates are not going to be available on Transifex.
    """
    local("pybabel extract -F website/frontend/babel.cfg -k lazy_gettext -o website/frontend/messages.pot website/frontend")
    print(green("Strings have been successfully extracted into messages.pot file.", bold=True))


def resync_po_files_from_pot():
    """[dev only]Resync .po files according to .pot file, not using Transifex"""
    local("pybabel update -i website/frontend/messages.pot -d website/frontend/translations/")
    print(green("Translations have been updated successfully.", bold=True))


def pull_translations():
    """Pull translations for languages defined in config from Transifex and compile them.

    Before using this command make sure that you properly configured Transifex client.
    More info about that is available at http://docs.transifex.com/developer/client/setup#configuration.
    """
    languages = ','.join(website.frontend.create_app().config['SUPPORTED_LANGUAGES'])
    local("tx pull -f -r picard-website.website -l %s" % languages)
    print(green("Translations have been updated successfully.", bold=True))


def update_strings():
    """Extract strings and pull translations from Transifex."""
    extract_strings()
    pull_translations()


def compile_translations():
    """Compile translations for use."""
    local("pybabel compile -d website/frontend/translations")
    print(green("Translated strings have been compiled and ready to be used.", bold=True))


def compile_styling():
    """Compile styles.less into styles.css.

    This command requires Less (CSS pre-processor). More information about it can be
    found at http://lesscss.org/.
    """
    local("./node_modules/.bin/gulp")
    print(green("Style sheets have been compiled successfully.", bold=True))


def plugins_generate():
    """Generate plugins.json and zipped plugin archive files

    Clone or pull repository from GitHub and run generate.py script
    """
    repo = website.frontend.create_app().config['PLUGINS_REPOSITORY']
    if not os.path.isdir(repo):
        print(yellow("'%s' directory defined by PLUGINS_REPOSITORY doesn't exist" % repo))
        if confirm("Do you want to clone picard-plugins from GitHub?"):
            local('git clone https://github.com/musicbrainz/picard-plugins/ %s' %
              repo)
        else:
            abort('Aborting...')
    with lcd(repo):
        local("git pull")
        local("python generate.py")
        print(green("Plugins files have been generated successfully.", bold=True))


def deploy():
    """Compile translations and styling."""
    compile_translations()
    compile_styling()


def reload():
    """Send HUP signal to uwsgi process to reload website (uwsgi server only)"""
    pidfile = '/tmp/picard.uwsgi.pid'
    try:
        with open(pidfile, 'rb') as f:
            pid = int(f.read().strip())
    except IOError as err:
        from errno import ENOENT
        if err.errno != ENOENT:
            abort(err)
        else:
            abort("Cannot find %s, is uwsgi running ?" % pidfile)
    except ValueError as err:
        abort("Cannot read a valid pid from %s (%s) !" % (pidfile, err))
    except Exception as err:
        abort(err)
    else:
        result = local("kill -HUP %d" % pid)
        if result.succeeded:
            print(green("HUP signal sent to uwsgi process", bold=True))
