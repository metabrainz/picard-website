// Gulp plugins
const { dest, parallel, series, src } = require('gulp')
const less = require('gulp-less')
const cleanCSS = require('gulp-clean-css')
const exec  = require('exec-chainable')
const del = require('del')

// Clean up existing files
function clean() {
  return del([ 'website/frontend/static/css' ])
}

// Compile less files to css
function styles() {
  return src('website/frontend/static/less/styles.less')
    .pipe(less())
    .pipe(cleanCSS())
    .pipe(dest('website/frontend/static/css'))
}

// Generate translation files
function translate() {
  return exec('pybabel compile -d website/frontend/translations')
}

exports.build = series(clean, styles)
exports.translate = translate
exports.deploy = parallel(exports.styles, translate)
exports.default = exports.deploy
