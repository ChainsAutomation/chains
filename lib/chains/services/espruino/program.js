//reset();

clearWatch();
clearInterval();

var blinking = [false, false, false];

function setBlink(index, enable) {
  if (blinking[index] && !enable) {
    LED[index].write(0);
  }
  blinking[index] = enable;
}

setInterval(function(e) {
  //print("TEMP", E.getTemperature());
  for(var i=0; i < blinking.length; i++) {
    if (blinking[i]) {
      LED[i].toggle();
    }
  }
}, 1000);

setWatch(function(e) {
    var len = e.time - e.lastTime;
    print("BTN", len);
    LED.toggle();
}, BTN, {edge:"falling", repeat:1, debounce:50});

