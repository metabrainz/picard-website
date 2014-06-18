// Gulp plugins
var gulp = require('gulp'),
    watch = require('gulp-watch'),
    connect = require('gulp-connect'),
    open = require('gulp-open'),
    clean = require('gulp-clean'),
    replace = require('gulp-replace'),
    minifycss = require('gulp-minify-css'),
    less = require('gulp-less');

// Create a webserver
gulp.task('webserver', function() {
  connect.server({
    livereload: true,
    root: ['.']
  });
});

// Compile less files to css
gulp.task('less', function() {
  return gulp.src('static/less/styles.less')
      .pipe(less())
      .pipe(gulp.dest('static/css'))
});

// Run tasks when files in 'static' directory change
gulp.task('watch', function() {
  gulp.watch('static/less/**', ['less']);
});

// Task for development
gulp.task('dev', ['less', 'watch', 'webserver'], function() {
  var options = {
    url: "http://localhost:8080",
    app: "firefox"
  };

  gulp.src("./index.html") //A file should exist
      .pipe(open("", options));
});

gulp.task('default', ['dev']);

// ##################################################################
//                        Build related tasks
// ##################################################################
// The goal is to be able to build and push to Github Pages (or our server.)
var buildDir = './_gh-pages';

// Copy files to push to server
gulp.task('copy-build', function() {
  gulp.src(['templates/*.html', './static/**'], {base: './'})
      .pipe(gulp.dest(buildDir));
});

// Compile less for server
gulp.task('less-server', ['copy-build'], function() {
  gulp.src('static/less/styles.less')
    .pipe(replace('/static/', '/picard-website/static/')) // Fixes FontAwesome font path issues
    .pipe(less())
    .pipe(minifycss())
    .pipe(gulp.dest(buildDir + '/static/css'));
});

// BUILD!
gulp.task('build', ['less-server']);
