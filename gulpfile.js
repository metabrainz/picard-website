// Gulp plugins
var gulp = require('gulp'),
    watch = require('gulp-watch'),
    connect = require('gulp-connect'),
    open = require('gulp-open'),
    clean = require('gulp-clean'),
    replace = require('gulp-replace'),
    minifycss = require('gulp-minify-css'),
    fileinclude = require('gulp-file-include'),
    less = require('gulp-less');

// Create a webserver
gulp.task('webserver', function() {
  connect.server({
    livereload: true,
    root: ['tmp']
  });
});

// Compile less files to css
gulp.task('less', function() {
  return gulp.src('static/less/styles.less')
      .pipe(less())
      .pipe(gulp.dest('tmp/static/css'))
      .pipe(connect.reload());
});

// Copy js files
gulp.task('js', function() {
  gulp.src('static/js/*.js')
    .pipe(gulp.dest('tmp/static/js'))
    .pipe(connect.reload());
});

// Include templates in html files
gulp.task('template', function() {
  return gulp.src(['*.html'])
    .pipe(fileinclude({
        prefix: '@@',
        basepath: '@file'
      }))
    .pipe(gulp.dest('tmp'))
    .pipe(connect.reload());
});

// Run tasks when files in 'static' directory change
gulp.task('watch', function() {
  gulp.watch('static/less/*.less', ['less']);
  gulp.watch('static/js/*.js', ['js']);
  gulp.watch('*.html', ['template']);
  gulp.watch('templates/*.html', ['template']);
})

// Copy files from the static directory to the tmp dir
gulp.task('copy-tmp', function() {
  gulp.src(['*.html', './static/**'], {base: './'})
      .pipe(gulp.dest('tmp'));
});

// Task for development
gulp.task('dev', ['copy-tmp', 'template', 'less', 'watch', 'webserver'], function() {
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
gulp.task('copy-build', ['copy-tmp', 'template'], function() {
  gulp.src(['tmp/*.html', './tmp/**'], {base: './tmp'})
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
