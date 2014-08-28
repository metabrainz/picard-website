// Gulp plugins
var gulp = require('gulp'),
    minifycss = require('gulp-minify-css'),
    less = require('gulp-less');

// Compile less files to css
gulp.task('less', function() {
    return gulp.src('static/less/styles.less')
        .pipe(less())
        .pipe(gulp.dest('static/css'))
});

gulp.task('default', ['less']);
