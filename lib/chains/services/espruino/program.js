//reset();

var buttonPresses = 0;
var lastButtonPressLength = 0;
var batteryPercentage = 0;
var temperatureLevel = 0;
var lightLevel = 0;

function updateAdvertisingData() {
  NRF.setAdvertising(
    {},
    {
      manufacturer: 0x0590,
      manufacturerData:[buttonPresses, lastButtonPressLength, batteryPercentage, temperatureLevel, lightLevel]
    }
  );
}

function readSensors() {
  batteryPercentage = Puck.getBatteryPercentage();
  temperatureLevel = E.getTemperature();
  lightLevel = parseInt(Math.round(Puck.light() * 100));
}

function flashLedsOnStartup() {
  LED1.write(0);
  LED2.write(0);
  LED3.write(0);
  setTimeout(function(){ digitalPulse(LED2, 1, 200); }, 300);
  setTimeout(function(){ digitalPulse(LED3, 1, 200); }, 600);
  digitalPulse(LED1, 1, 200);
}

clearWatch();
clearInterval();
clearTimeout();

readSensors();
updateAdvertisingData();

setWatch(function(e) {
  lastButtonPressLength = (e.time - e.lastTime) * 10;
  buttonPresses++;
  digitalPulse(LED2, 1, 200);
  updateAdvertisingData();
}, BTN, {edge:"falling", repeat:1, debounce:50})

setInterval(function() {
    readSensors();
    updateAdvertisingData();
}, interval * 1000);

flashLedsOnStartup();
