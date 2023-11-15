const noble = require("@abandonware/noble");

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
function callback_(error, services, characteristics) {
  console.log('ALL', error, services, characteristics);
  
}

module.exports = class Device {
  constructor(uuid) {
    this.uuid = uuid;
    this.connected = false;
    this.power = false;
    this.brightness = 100;
    this.hue = 0;
    this.saturation = 0;
    this.l = 0.5;
    this.peripheral = undefined;

    noble.on("stateChange", (state) => {
      console.log("State:", state);
      if (state == "poweredOn") {
        noble.startScanningAsync();
        console.log('Starting scanning...');
      } else {
        try{
          if (this.peripheral) this.peripheral.disconnect();
        } catch (e) {
          console.log(e);
        }
        
        this.connected = false;
      }
    });

    noble.on("discover", async (peripheral) => {
      console.log('Discovered:', peripheral.uuid, peripheral.advertisement.localName);
      if (peripheral.uuid == this.uuid) {
        console.log('Found!')
        this.peripheral = peripheral;
        await peripheral.connectAsync();
        console.log('Connected!');
        noble.stopScanning();
      }
    });
  }



  async connectAndGetWriteCharacteristics() {

    console.log('trying to connect and get write characteristics');
    if (this.connected){
      console.log('already connected');
    }
    if (!this.peripheral) {
      try {
        noble.startScanningAsync();
      } catch (e) {
        console.log('Error starting scanning... need to wait');
      }
      return;
    }
    console.log('[OK] this.perepheral is not null');
    await this.peripheral.connectAsync();
    console.log('[OK] Connected');
    this.connected = true;
    console.log('Discovering characteristics...');
    // await this.peripheral.discoverAllServicesAndCharacteristics(callback_);
    const { characteristics } =
      await this.peripheral.discoverSomeServicesAndCharacteristicsAsync(
        ["fff0"],
        ["fff3"]
      );
    console.log('SET UP WRITE CHARACTERISTICS!', characteristics);
    this.write = characteristics[0];
  }

  async disconnect() {
    console.log('disconnecting...');
    if (this.peripheral) {
      await this.peripheral.disconnectAsync();
      this.connected = false;
    }
  }

  async set_power(status) {
    if (!this.connected) await this.connectAndGetWriteCharacteristics();
    if (this.write) {
      const buffer = Buffer.from(
        `7e0004${status ? "01" : "00"}00000000ef`,
        "hex"
      );
      console.log("Write:", buffer);
      this.write.write(buffer, true, (err) => {
        if (err) console.log("Error:", err);
        this.power = status;
        this.disconnect();
      });
    } else {
      console.log('No this.write');
    }
  }

  async set_brightness(level) {
    if (level > 100 || level < 0) return;
    if (!this.connected) await this.connectAndGetWriteCharacteristics();
    if (this.write) {
      const level_hex = ("0" + level.toString(16)).slice(-2);
      const buffer = Buffer.from(`7e0001${level_hex}00000000ef`, "hex");
      console.log("Write:", buffer);
      this.write.write(buffer, true, (err) => {
        if (err) console.log("Error:", err);
        this.brightness = level;
        this.disconnect();
      });
    } else {
      console.log('No this.write');
    }
  }

  async set_rgb(r, g, b) {
    if (!this.connected) await this.connectAndGetWriteCharacteristics();
    if (this.write) {
      const rhex = ("0" + r.toString(16)).slice(-2);
      const ghex = ("0" + g.toString(16)).slice(-2);
      const bhex = ("0" + b.toString(16)).slice(-2);
      const buffer = Buffer.from(`7e000503${rhex}${ghex}${bhex}00ef`, "hex");
      console.log("Write:", buffer);
      this.write.write(buffer, true, (err) => {
        if (err) console.log("Error:", err);
        this.disconnect();
      });
    } else {
      console.log('No this.write');
    }
  }

  async set_hue(hue) {
    if (!this.connected) await this.connectAndGetWriteCharacteristics();
    if (this.write) {
      this.hue = hue;
      const rgb = hslToRgb(hue / 360, this.saturation / 100, this.l);
      this.set_rgb(rgb[0], rgb[1], rgb[2]);
      this.disconnect();
    } else {
      console.log('No this.write');
    }
  }

  async set_saturation(saturation) {
    if (!this.connected) await this.connectAndGetWriteCharacteristics();
    if (this.write) {
      this.saturation = saturation;
      const rgb = hslToRgb(this.hue / 360, saturation / 100, this.l);
      this.set_rgb(rgb[0], rgb[1], rgb[2]);
      this.disconnect();
    } else {
      console.log('No this.write');
    }
  }
};
