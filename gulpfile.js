// Gulp plugins
var gulp = require('gulp'),
    minifycss = require('gulp-minify-css'),
    less = require('gulp-less');

// Compile less files to css
gulp.task('less', function() {
    return gulp.src('website/frontend/static/less/styles.less')
        .pipe(less())
        .pipe(gulp.dest('website/frontend/static/css'))
});

gulp.task('default', ['less']);
