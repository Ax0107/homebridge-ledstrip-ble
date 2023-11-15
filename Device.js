const axios = require('axios');

function hslToRgb(h, s, l) {
  var r, g, b;

  if (s == 0) {
    r = g = b = l; // achromatic
  } else {
    var hue2rgb = function hue2rgb(p, q, t) {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    };

    var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    var p = 2 * l - q;
    r = hue2rgb(p, q, h + 1 / 3);
    g = hue2rgb(p, q, h);
    b = hue2rgb(p, q, h - 1 / 3);
  }

  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}
function remoteSetColor(color, brightness){

  axios({
    method: 'post',
    url: 'http://localhost:9988/set/',
    data: {
      color: color,
      brightness: brightness
    }
  })
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.log(error);
  });
}

function remoteSetPower(status){

  axios({
    method: 'post',
    url: 'http://localhost:9988/set_state/',
    data: {
      status: status,
    }
  })
  .then(response => {
    console.log(response.data);
    
  })
  .catch(error => {
    console.log(error);
  });
}


module.exports = class Device {
  constructor(uuid) {
    this.uuid = uuid;
    this.power = false;
    this.brightness = 100;
    this.hue = 0;
    this.saturation = 0;
    this.l = 0.5;
  }

  async set_power(status) {
    console.log("Write power:", status);
    remoteSetPower(status);
    this.power = status;
  }

  async set_brightness(level) {
    if (level > 100 || level < 0) return;
    console.log("Write brightness:", level);
    remoteSetColor(-1, level);
    this.brightness = level;
  }

  async set_rgb(r, g, b) {
    const rhex = ("0" + r.toString(16)).slice(-2);
    const ghex = ("0" + g.toString(16)).slice(-2);
    const bhex = ("0" + b.toString(16)).slice(-2);
    console.log("Write color:", `${rhex}${ghex}${bhex}`);
    remoteSetColor(`${rhex}${ghex}${bhex}`, -1);
  }

  async set_hue(hue) {
    this.hue = hue;
    const rgb = hslToRgb(hue / 360, this.saturation / 100, this.l);
    this.set_rgb(rgb[0], rgb[1], rgb[2]);
    this.hue = hue;
  }

  async set_saturation(saturation) {
    this.saturation = saturation;
    const rgb = hslToRgb(this.hue / 360, saturation / 100, this.l);
    this.set_rgb(rgb[0], rgb[1], rgb[2]);
    this.saturation = saturation;
  }
};
