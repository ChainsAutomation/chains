//reset();

clearWatch();
clearInterval();

var blinking = [null, false, false, false];

function setBlink(index, enable) {
  if (blinking[index] && !enable) {
    switch (index) {
      case 1: LED1.write(0); break;
      case 2: LED2.write(0); break;
      case 3: LED3.write(0); break;
    }
  }
  if (!blinking[index] && enable) {
    switch (index) {
      case 1: LED1.write(1); break;
      case 2: LED2.write(1); break;
      case 3: LED3.write(1); break;
    }
  }
  blinking[index] = enable;
}

function sendState(key, type, value) {
  print("#st#" + key + ";" + type + ";" + value + "#/st#");
}

function sendAllState() {
  sendState("temperature", "f", E.getTemperature());
  sendState("light", "f", Puck.light());
  sendState("battery", "f", Puck.getBatteryPercentage());
}

setInterval(function(e) {
  if (blinking[1]) {
    LED1.toggle();
  }
  if (blinking[2]) {
    LED2.toggle();
  }
  if (blinking[3]) {
    LED3.toggle();
  }
}, 1000);

setInterval(function(e) {
  sendAllState();
}, 30000);

setWatch(function(e) {
    var len = e.time - e.lastTime;
    sendState("button", "b", len);
}, BTN, {edge:"falling", repeat:1, debounce:50});

sendAllState();
