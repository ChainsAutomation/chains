$(document).ready(function(){

    var app = new window.Chains.App();

    // Example - configure different backend url
    // app.configure('restUrl', 'http://webapi.my-chains.com');
    // app.configure('socketUrl', 'http://socketio.my-chains.com');

    app.start();

});
/*
requirejs([""], function(util) {
    //This function is called when scripts/helper/util.js is loaded.
    //If util.js calls define(), then this function is not fired until
    //util's dependencies have loaded, and the util argument will hold
    //the module value for "helper/util".
});
*/
