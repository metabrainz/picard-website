// Gulp plugins
const { dest, parallel, series, src } = require('gulp')
const less = require('gulp-less')
const cleanCSS = require('gulp-clean-css')
const exec  = require('child-process-promise').exec
const del = require('del')

function log_exec_output(result) {
  if (result.stdout) console.log(result.stdout)
  if (result.stderr) console.error(result.stderr)
}

function clean() {
  return del([ 'website/frontend/static/css' ])
}
clean.description = 'Clean up existing files'

function styles() {
  return src('website/frontend/static/less/styles.less')
    .pipe(less())
    .pipe(cleanCSS())
    .pipe(dest('website/frontend/static/css'))
}
styles.description = 'Compile less files to css'

function translate() {
  return exec('pybabel compile -d website/frontend/translations')
    .then(log_exec_output)
}
translate.description = 'Compile translations for use'

function extract_strings() {
  return exec('pybabel extract -F website/frontend/babel.cfg -k lazy_gettext -o website/frontend/messages.pot website/frontend')
    .then(log_exec_output)
}
extract_strings.description = 'Extract all strings into messages.pot'

function resync_po_files_from_pot() {
  return exec('pybabel update -i website/frontend/messages.pot -d website/frontend/translations/')
    .then(log_exec_output)
}
resync_po_files_from_pot.description = '[dev only] Resync .po files according to .pot file, not using Transifex'

async function pull_translations() {
  const languages = await exec("python -c \"import website.frontend; print(','.join(website.frontend.create_app().config['SUPPORTED_LANGUAGES']))\"")
  return exec(`tx pull -f -r picard-website.website -l ${languages}`)
    .then(log_exec_output)
}
pull_translations.description = 'Pull translations for languages defined in config from Transifex and compile them'

exports.clean = clean
exports.styles = styles
exports.translate = translate
exports.extract_strings = extract_strings
exports.resync_po_files_from_pot = resync_po_files_from_pot
exports.pull_translations = pull_translations

exports.update_strings = series(extract_strings, pull_translations)
exports.update_strings.description = 'Extract strings and pull translations from Transifex'
exports.build = parallel(series(clean, styles), translate)

exports.default = exports.build
