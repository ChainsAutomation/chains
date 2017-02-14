export function dtype(data) {
  /*
  console.log('device type');
  console.log(data);
  */
  if (typeof(data) !== "object") {
    console.log("bad device data" + data);
    data = {};
  }
  if (!data.hasOwnProperty('type')) {
    data.type = 'unknown';
  }
  //console.log("device type: " + data.type);
  let newdata = {};
  switch(data.type) {
    case "time":
      return devTimer(data);
    case "temperature":
      return devTemperature(data);
      // console.log(JSON.stringify(newdata));
    case "humidity":
      return devHumidity(data);
    case "lamp":
      return devLight(data);
    case "light":
      return devLight(data);
    default:
      return devUnknown(data);
  }
}

export function devUnknown(data) {
  return Object.assign({},
    data, {
    icon: 'icons/awesome/question-circle-o.svg',
    name: 'unknown, yo'
  })
}

export function devLight(data) {
  return Object.assign({},
    data, {
    icon: 'icons/awesome/lightbulb-o.svg',
    name: 'light, yo'
  })
}

export function devTimer(data) {
  return Object.assign({},
    data, {
      icon: 'icons/windows/clock.svg',
      name: 'timer, yo'
   })
}

export function devTemperature(data) {
  return Object.assign({},
    data, {
      icon: 'icons/weather/thermometer.svg',
      name: 'temperature, yo'
   })
}

export function devHumidity(data) {
  return Object.assign({},
    data, {
      icon: 'icons/weather/humidity.svg',
      name: 'humidity, yo'
   })
}
