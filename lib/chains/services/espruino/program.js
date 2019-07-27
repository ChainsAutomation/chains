//reset();

var buttonPresses = 0;
var batteryPercentage = 0;
var temperatureLevel = 0;
var lightLevel = 0;

function updateAdvertisingData() {
  NRF.setAdvertising(
    {},
    {
      manufacturer: 0x0590,
      manufacturerData:[buttonPresses, batteryPercentage, temperatureLevel, lightLevel]
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

setWatch(function() {
  buttonPresses++;
  digitalPulse(LED2, 1, 200);
  updateAdvertisingData();
}, BTN, {edge:"rising", repeat:1, debounce:20})

setInterval(function() {
    readSensors();
    updateAdvertisingData();
}, interval * 1000);

flashLedsOnStartup();
