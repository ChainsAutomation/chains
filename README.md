#Chains

Chains is a home automation system.

The main goals of the Chains project are:
* Support as many different devices as possible
* Easy device development
* Easy installation

While most home automation software focuses on supporting a single piece of hardware, we aim to support them all and make them work together.

##What are nodes, devices and services?

In the Chains documentation we often refer to nodes, devices and services, these are explained below.

###Node
Nodes are computers runnning Chains. Multiple machines are supported, and communicate on a regular tcp/ip network.

###Device
A `device` is a program that controls something in chains, usually a piece of hardware or internet service.
Example devices: PhilipsHue, onewire, timer, pushover.

###Service
A service is a specific piece of functionality exposed on a `device`. A single device be able to do several `actions` and report several `events`. We call these "sub-devices" services. E.g. "the bluetooth device exposes an Obex service"

##What are events, actions and rules?

While nodes, devices and services deals with the software controlling hardware sensors and such; events, actions and rules are what makes it possible for the former to connect and cooperate.

###Event
A `device` will often report changes or things that happen to the system. This is called an `event`.
A remote control device would send an event when a button is pressed, a temperature sensor device would send an event containing the current temperature and so on.

###Action
Some devices are able to do things as well as report `events` these are called actions.
A receiver device could have actions like PowerOn, ChangeSource and Mute, while a light control device could have actions like LightOn, LightOff and AllOff.

###Rule
A `rule` is a description of what should happen as a response to an `event` in the system. These rules can be chained together to create more advanced logic. Example in pseudo code:
```
if event('open_door') -> action(all_lights_on) and action(play_radio)
```
The simplest rules can be easily created in the upcoming webgui, while for advanced applications the full power of the python programming langauge is available.

###Supported platforms
* Linux on Raspberry Pi and Raspberry Pi 2
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
* USB-Relay
* System-information

**In development:**
* OneWire
* Onkyo receiver control
* Spotify
* mpd
* xmms2
* Micropython
* Asterisk (voip)
* Motion

#Installation

We will eventually provide docker images from the docker registry, but for now dockerfiles can be created by bin/dockerfile-assemble.py and built on your own system.
Docker is a good match for our project since we need a host of different libraries and services running to support the different devices. Providing instructions for all distributions and testing these configurations would be too time consuming. The whole process, however, is described in the generated dockerfile. Feel free to install it locally.

#Development

We aim at making development of new devices as easy as possible.
While it is possible to write everything from scratch, we provide a framework that takes care of common functions and hides unnecessary boilerplate.

```python
import chains.device

class MynewDevice(chains.device.Device):
  def onInit(self):
    code which runs at device startup
  
  def action_something(self, myparam):
    """
    Do something
    @param   myparam  string  A string needed for this action
    """
    action_code_goes_here

```

The above code will create description of the action "something" on the "Mynew"-device and announce it to the Chains system. For now the best way to write devices is to model them after the existing devices, PhilipsHue is a good place to start.
We will eventually document this in our wiki.

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
