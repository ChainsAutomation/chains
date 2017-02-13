require.config({
    paths: {
        jquery: 'jquery.min',
        bootstrap: 'bootstrap.min',
        routie: 'routie.min',
        moment: 'moment.min',
        'socket.io': '/api/socket.io/socket.io'
    },

    shim: {
        routie: {
            exports: 'routie'
        },
        bootstrap: {
            deps: ['jquery']
        }
    }
});
requirejs(['app'], function(App) {
    //This function is called when scripts/helper/util.js is loaded.
    //If util.js calls define(), then this function is not fired until
    //util's dependencies have loaded, and the util argument will hold
    //the module value for "helper/util".

    var app = new App();

    // Example - configure different backend url
    // app.configure('restUrl', 'http://webapi.my-chains.com');
    // app.configure('socketUrl', 'http://socketio.my-chains.com');

    app.start();
});
