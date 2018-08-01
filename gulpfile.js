// Gulp plugins
var gulp = require('gulp');
var less = require('gulp-less');
var cleanCSS = require('gulp-clean-css');
var del = require('del');

// Clean up existing files
function clean() {
  return del([ 'website/frontend/static/css' ]);
}

// Compile less files to css
function styles() {
  return gulp.src('website/frontend/static/less/styles.less')
    .pipe(less())
    .pipe(cleanCSS())
    .pipe(gulp.dest('website/frontend/static/css'))
}

var build = gulp.series(clean, styles);
gulp.task('default', build);
