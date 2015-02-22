#Chains

Chains is a home automation system.

The main goal of the Chains project is to support as many different devices as possible, eventually make it easy to use and to make developing support for new devices easy. 

###What are nodes, devices and services?

In the Chains documentation we often refer to nodes, devices and services, these are explained below.

**Node**
Nodes are computers runnning Chains. Multiple machines are supported, and communicate on a regular tcp/ip network.

**Device**
A device is a program that controls something in chains, usually a piece of hardware or internet service.
Example devices: PhilipsHue, 

**Service**
A service is a specific piece of functionality exposed on a `device`. A single device be able to do several `actions` and report several `events`. We call these "sub-devices" services. E.g. "the bluetooth device exposes an Obex service"

###What are events, actions and rules?

**Event**
A `device` will often report changes or things that happen to the system. This is called an `event`.
A remote control device would send an event when a button is pressed, a temperature sensor device would send an event containing the current temperature and so on.

**Action**
Some devices are able to do things as well as report `events` these are called actions.
A receiver device could have actions like PowerOn, ChangeSource and Mute, while a light control device could have actions like LightOn, LightOff and AllOff.

###Supported platforms

* Linux on Raspberry Pi
* Linux on x86 (32/64bit)

###Supported devices (sensors, relays etc)
* Phidgets
* Philips Hue
* rrd (graphing)
* Bluetooth
* Tellstick
* Pushover.net
* IR remote control (lirc)
* Time
* IRC
* LGTV

In development:
* OneWire
* Onkyo receiver control
* Spotify
* mpd
* xmms2
* Micropython
* USB-Relay
* Asterisk (voip)
* Motion

#Installation

#Development

#Contact

You can find us in the `#chains` channel on the `Freenode` IRC network.

#Tech
Chains is a grateful user of a number of great open source projects:
* Python
* PYPY
* NodeJS
* RabbitMQ
* Docker
* Supervisor
* Raspian and Ubuntu (for docker images)
* Bluez
* A number of python libraries

`TODO: Expand this list and add links to projects`
