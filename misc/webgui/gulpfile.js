var gulp = require('gulp'), 
    sass = require('gulp-ruby-sass'),
    notify = require("gulp-notify"),
    bower = require('gulp-bower'),
	minifycss = require('gulp-minify-css'),
	rename = require('gulp-rename');


var config = {
    sassDir: './app/sass',
    bowerDir: './bower_components',
    distDir: './public'
}

gulp.task('bower', function() { 
    return bower()
         .pipe(gulp.dest(config.bowerDir)) 
});

gulp.task('icons', function() { 
    return gulp.src(config.bowerDir + '/fontawesome/fonts/**.*') 
        .pipe(gulp.dest(config.distDir + '/fonts')); 
});

gulp.task('css', function() { 
	return sass(config.sassDir + '/style.scss', {
        style: 'compressed',
        loadPath: [
          config.sassDir,
          config.bowerDir + '/bootstrap-sass-official/assets/stylesheets',
          config.bowerDir + '/fontawesome/scss',
        ]
    }) 
    .on("error", sass.logError)
    .pipe(gulp.dest(config.distDir + '/css'))
    .pipe(rename({suffix: '.min'}))
	.pipe(minifycss())
	.pipe(gulp.dest(config.distDir + '/css'));
});

// Rerun the task when a file changes
gulp.task('watch', function() {
     gulp.watch(config.sassPath + '/**/*.scss', ['css']); 
});

gulp.task('default', ['bower', 'icons', 'css']);
