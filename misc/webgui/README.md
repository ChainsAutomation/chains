# HOWTO

Since this webgui is in its early stages, we haven't yet automated its setup in chains.

If you want to try it during the development period, do as follows:

* Edit src/config.example.js to point to the master running chains, and copy it to config.js in the same directory
* Run `npm install` in the root directory
* Run `webpack` in the root directory
* Make the webgui available through a web-server, easy option: `python3 -m http.server` in the root directory
