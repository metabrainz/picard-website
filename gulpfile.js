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
  gulp.src('static/less/styles.less')
    .pipe(less())
    .pipe(gulp.dest('static/css'));
});

// Watch files for changes and reload our server
gulp.task('livereload', function() {
  gulp.src(['*.html', 'static/css/*.css', 'static/js/*.js'])
    .pipe(watch())
    .pipe(connect.reload());
});

// Run the 'less' task when files change
gulp.task('watch', function() {
  gulp.watch('static/less/styles.less', ['less']);
})

// Task for development
gulp.task('dev', ['less', 'livereload', 'watch', 'webserver'], function() {
  var options = {
    url: "http://localhost:8080",
    app: "firefox"
  };

  gulp.src("./index.html") //A file should exist
      .pipe(open("", options));
});

gulp.task('default', ['dev']);

// Build related tasks
// The goal is to be able to build and push to Github Pages (or our server.)
var buildDir = './_gh-pages';

// Copy files to push to server
gulp.task('copy', function() {
  gulp.src(['*.html', './static/**'], {base: './'})
      .pipe(gulp.dest(buildDir));
});

// Compile less for server
gulp.task('less-server', ['copy'], function() {
  gulp.src('static/less/styles.less')
    .pipe(replace('/static/', '/picard-website/static/')) // Fixes FontAwesome font path issues
    .pipe(less())
    .pipe(minifycss())
    .pipe(gulp.dest(buildDir + '/static/css'));
});

gulp.task('remove-less', ['less-server'], function() {
  gulp.src(buildDir + '/static/less', {read: false})
      .pipe(clean());
});

// BUILD!
gulp.task('build', ['remove-less']);
