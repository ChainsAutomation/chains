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
  if (Puck.getBatteryPercentage() < 30) {
    setBlink(3, true);
  }
}

var blinkState = false;
setInterval(function(e) {
  blinkState = !blinkState;
  if (blinking[1]) {
    LED1.write(blinkState);
  }
  if (blinking[2]) {
    LED2.write(blinkState);
  }
  if (blinking[3]) {
    LED3.write(blinkState);
  }
}, 1000);

setInterval(function(e) {
  sendAllState();
}, 30000);

setWatch(function(e) {
    var len = e.time - e.lastTime;
    if (len > 3) {
      //sendState("button", "s", "status");
      //sendState("button", "f", len);
      var lev = Puck.getBatteryPercentage();
      var l = null;
      if (lev > 80) {
        l = LED2;
      } else if (lev > 40) {
        l = LED3;
      } else {
        l = LED1;
      }
      digitalPulse(l, 1, 200);
      digitalPulse(l, 0, 200);
      digitalPulse(l, 1, 200);
      digitalPulse(l, 0, 200);
      digitalPulse(l, 1, 200);
    } else if (len > 0.6) {
      sendState("button", "s", "long");
      //sendState("button", "f", len);
      digitalPulse(LED1, 1, 200);
    } else {
      sendState("button", "s", "short");
      //sendState("button", "f", len);
      digitalPulse(LED2, 1, 200);
    }
}, BTN, {edge:"falling", repeat:1, debounce:50});

LED1.write(0);
LED2.write(0);
LED3.write(0);
sendAllState();
digitalPulse(LED2, 1, 200);
digitalPulse(LED2, 0, 200);
digitalPulse(LED2, 1, 200);
digitalPulse(LED2, 0, 200);
digitalPulse(LED2, 1, 200);
