var gulp = require('gulp'),
  connect = require('gulp-connect'),
  watch = require('gulp-watch'),
  less = require('gulp-less'),
  coffee = require('gulp-coffee');

gulp.task('webserver', function() {
  connect.server({
    livereload: true,
    root: ['.']
  });
});

gulp.task('livereload', function() {
  gulp.src(['index.html', 'static/css/*.css', 'static/js/*.js'])
    .pipe(watch())
    .pipe(connect.reload());
});

gulp.task('less', function() {
  gulp.src('static/less/*.less')
    .pipe(less())
    .pipe(gulp.dest('static/css'));
});

gulp.task('watch', function() {
  gulp.watch('static/less/*.less', ['less']);
  // gulp.watch('scripts/*.coffee', ['coffee']);
})

/*gulp.task('coffee', function() {
  gulp.src('scripts/*.coffee')
    .pipe(coffee())
    .pipe(gulp.dest('.tmp/scripts'));
});
*/

gulp.task('default', ['less', 'livereload', 'watch', 'webserver']);
