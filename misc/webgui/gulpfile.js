var gulp = require('gulp'), 
    sass = require('gulp-ruby-sass'),
    notify = require("gulp-notify"),
    bower = require('gulp-bower'),
	minifycss = require('gulp-minify-css'),
	rename = require('gulp-rename'),
    fileinclude = require('gulp-file-include'),
    rimraf = require('gulp-rimraf'),
    concat = require('gulp-concat');

var config = {
    sassDir:  './app/sass',
    imgDir:   './app/images',
    jsDir:    './app/js',
    bowerDir: './bower_components',
    distDir:  './public',
    htmlDir:  './app/html'
}

gulp.task('bower', function() { 
    return bower()
         .pipe(gulp.dest(config.bowerDir)) 
});

gulp.task('icons', function() { 
    return gulp.src(config.bowerDir + '/fontawesome/fonts/**.*') 
        .pipe(gulp.dest(config.distDir + '/fonts')); 
});

gulp.task('images', function() { 
    return gulp.src(config.imgDir + '/**/**.*') 
        .pipe(gulp.dest(config.distDir + '/images'));
});

gulp.task('css', function() { 
	return sass(config.sassDir + '/app.scss', {
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

gulp.task('js:app', function() {

    // App

    return gulp.src([
        config.jsDir + '/**/*.js'
    ])
    .pipe(concat('app.js'))
    .pipe(gulp.dest(config.distDir + '/js'));

});

gulp.task('js:config', function() {

    // Config

    return gulp.src([
        './app/config.js'
    ])
    .pipe(gulp.dest(config.distDir + '/js'));

});

gulp.task('js:vendor', function() {

    // Vendor

    return gulp.src([
        config.bowerDir + '/jquery/dist/*.min.*',
        config.bowerDir + '/html5shiv/dist/html5shiv.min.js',
        config.bowerDir + '/respond/dest/respond.min.js',
        config.bowerDir + '/bootstrap/dist/js/*.min.*',
        config.bowerDir + '/knockout/dist/knockout.js',
        config.bowerDir + '/routie/dist/routie.min.js',
        config.bowerDir + '/moment/min/*.min.js',
        config.bowerDir + '/moment-timezone/moment-timezone.js'
    ])
    .pipe(gulp.dest(config.distDir + '/js'));

});

gulp.task('js', ['js:app','js:vendor','js:config'], function(){ });

gulp.task('html', function() {
    gulp.src([
        config.htmlDir + '/*.html'
    ])
    .pipe(fileinclude({
        prefix: '@@',
        basepath: '@file'
    }))
    .pipe(gulp.dest(config.distDir));
});

gulp.task('clean', function () {
  return gulp.src([
    config.distDir + '/{js,css,fonts}/**/*',
    config.distDir + '/index.html'
  ])
  .pipe(rimraf());
});

// Rerun the task when a file changes
gulp.task('watch', function() {
    gulp.watch(config.sassPath + '/**/*.scss', ['css']); 
    gulp.watch(config.jsDir + '/**/*.js', ['js']);
    gulp.watch(config.htmlDir + '/*/**.html', ['html']);
});

gulp.task('default', ['clean'], function(){
    gulp.run('bower');
    gulp.run('icons');
    gulp.run('css');
    gulp.run('js:vendor');
    gulp.run('js:app');
    gulp.run('js:config');
    gulp.run('images');
    gulp.run('html');
});
