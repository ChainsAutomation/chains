[![Build Status](https://img.shields.io/travis/ChainsAutomation/chains.svg)](https://travis-ci.org/ChainsAutomation/chains)
[![GitHub forks](https://img.shields.io/github/forks/ChainsAutomation/chains.svg)]()
[![GitHub stars](https://img.shields.io/github/stars/ChainsAutomation/chains.svg)]()
[![IRC](https://img.shields.io/badge/freenode-%23chains-blue.svg)](http://webchat.freenode.net/?channels=chains)

#Chains

Chains is a home automation system.

The main goals of the Chains project are:
* Support as many different services as possible
* Easy service development
* Easy installation

While most home automation software focuses on supporting a single piece of hardware, we aim to support them all and make them work together.

##Supported platforms
* Linux on Raspberry Pi and Raspberry Pi 2
* Linux on x86 (32/64bit)

##Supported services (sensors, relays etc)
* Phidgets
* Philips Hue
* InfluxDB (graphing)
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
* Mail
* Network proximity
* Raspberry Pi (GPIOs and camera)
* CEC (Raspberry Pi and Pulse Eight usb-adapter)
* Mouse (usb, buttons and direction)
* USB-info
* Keyboard (usb, click, release, modifiers)
* Sonos
* Integra and Onkyo receivers

**In development:**
* IPCam
* OneWire
* Spotify
* mpd
* xmms2
* Micropython
* Asterisk (voip)
* Motion

#Installation

We will eventually provide docker images from the docker registry, but for now dockerfiles can be created by bin/dockerfile-assemble.py and built on your own system.
Docker is a good match for our project since we need a host of different libraries and daemons running to support the different services. Providing instructions for all distributions and testing these configurations would be too time consuming. The whole process, however, is described in the generated dockerfile. Feel free to install it locally.

#### Docker install for chains master (prebuilt image from docker hub)
```sh
# Create config and data dir:
sudo sh -c "mkdir -p /etc/chains/services && mkdir -p /srv/chains-data"

# Pull and run latest version
sudo docker run -d --privileged --net=host -v /etc/chains:/etc/chains -v /srv/chains-data:/srv/chains/data -v /dev:/dev -v /etc/localtime:/etc/localtime:ro chains/chains-master
```

####Docker build/install for chains master node
```sh
# Create config and data dir:
sudo sh -c "mkdir -p /etc/chains/services && mkdir -p /srv/chains-data"

# Create chains master image:
bin/dockerfile-assemble.py master
sudo docker build --no-cache -t chains/chains-master .

# Run chains master
sudo docker run -d --privileged --net=host -v /etc/chains:/etc/chains -v /srv/chains-data:/srv/chains/data -v /dev:/dev -v /etc/localtime:/etc/localtime:ro chains/chains-master
```


####Docker build/install for chains slave node (only if you already have a master node running on different computer)
```sh
# Create config and data dir:
sudo sh -c "mkdir -p /etc/chains/services && mkdir -p /srv/chains/data"

# Create chains slave image:
bin/dockerfile-assemble.py slave
sudo docker build --no-cache -t chains/chains-slave .

# Run chains slave
# Exchange 192.168.1.1 for the ip address of your machine running chains-master
sudo docker run -d --privileged --net=host -e "AMQP=192.168.1.1:5672" -v /etc/chains:/etc/chains -v /srv/chains-data:/srv/chains/data -v /dev:/dev -v /etc/localtime:/etc/localtime:ro chains/chains-slave
```

# The `chains` command line application

Chains comes with the aptly named `chains` command line application.
When using docker this program will work automatically.

It is sometimes useful to run it from a computer that is not a node in the chains network, fortunately this is pretty easy if you know linux basics:
* clone the chains repository into /srv/chains as described above
* symlink /srv/chains/lib/chains into your python site-packages dir
* add /srv/chains/bin to your path
* create /etc/chains/amqp.conf with the same content as your other nodes (host/port pointing to master)
The 3 first steps are only necessary because our setup.py is (probably, not tested) not working properly at the moment, sorry!

# Chains intro

##What are nodes(master/slave), services, devices and properties?

In the Chains documentation we often refer to nodes, devices and services, these are explained below.

###Node
Nodes are computers runnning Chains. Multiple machines are supported, and they communicate on a regular tcp/ip network using an included RabbitMQ-server. If you run chains on only one machine you must run the "master" node, this is the hub of the chains system and it takes cares of the `rules` described below. Slave nodes are installed on additional computers that you may add to the chains network.

### Service
A `service` is a program that controls something in chains, usually a piece of hardware like a light controller or internet service like pushover.net.
Example services: PhilipsHue, onewire, timer, pushover.

###Device
Devices are how functionality is divided into units in a `service`. In a service that control light switches, each light switch would typically be a `device`. A device may be able to do several `actions` and report several `events`.

###Property
Properties are information made available from a `device`. A light switch device could for example have the properties 'dimlevel', 'power' and 'location'. A property can also be the target of an `action`, if the property is something that can be change. An example of this would be the "power" property on a light switch `device`, that might switch between "on" and "off".

Nodes, Services, Devices and Properties for a tree-like structure:
```
Node (computer)
   \ Service1
   |    \ Device1
   |    |        \ Property1
   |    |        \ Property2
   |    \ Device2
   |             \ Property1
   |
   \Service2
   |    \ Device1
   |    \ Device2

and so on
```

##What are events, actions and rules?

While nodes, services and devices deal with the software controlling hardware sensors and such; events, actions and rules are what makes it possible for the former to connect and cooperate.

###Event
A `device` will often report changes or things that happen in the system. This is called an `event`.
A remote control device would send an event when a button is pressed, a temperature sensor device would send an event containing the current temperature and so on.

###Action
Some devices are able to do things as well as report `events` these are called actions.
A receiver device could have actions like PowerOn, ChangeSource and Mute, while a light switch device might have actions like LightOn, LightOff and Dim.

###Rule
A `rule` is a description of what should happen as a response to an `event` in the system. These rules can be `chain`ed together to create more advanced logic.

The simplest `rules` can be easily created in the upcoming webgui, while for advanced applications the full power of the python programming langauge is available. Special objects are created to represent `events`, `actions` and current `state` in the chains system to simplify creation of `rules`.

####Example if written by hand
```python
# TODO: change to match new service/device naming
def rule(context):
   # wait for 'switch-2' event sent from 'device' on 'service_id'
   yield Event(service='service_id', device='switch-2')
   # run action 'power_off' on device 'other_device'
   Action(service='other_service', device='some_device', action='power_off')
   # and so on
   Action(...)
   yield Event(...)
   Action(...)
```

#Development

We aim at making development of new devices as easy as possible.
While it is possible to write everything from scratch, we provide a framework that takes care of common functions and hides unnecessary boilerplate.

```python
from chains.service import Service

class MynewService(Service):
  def onInit(self):
    # code that runs on service startup, usually setting things up for onStart below
    # get some config:
    self.username = self.config['username']
   
  def onStart(self):
    """main loop for the service"""
    while not self._shutdown:
      do_stuff_here
      # perhaps send an event:
      self.sendEvent('event_name', {'foo': {'value': 'bar', 'actions': ['refoo', 'unfoo'] } }, {'type': 'foo_event', 'location': 'home'})
   
  def action_unfoo(self, myparam):
    """
    Do something
    @param   myparam  string  A string is needed for this action
    """
    action_code_goes_here

```

The above code will create description of the action "unfoo" on the "Mynew"-service and announce it to the Chains system. For now the best way to write services is to model them after the existing services, PhilipsHue, Tellstck and System are good places to start.
We will eventually document this fully in our wiki.

## Mount chains repository from outside the container

To be able to use all your regular development tools and quickly test changes on a running system, mount the chains repositry into the chains container:

```sh
git clone git@github.com:ChainsAutomation/chains.git /srv/chains
docker pull chains/chains-master
docker run -d --privileged --net=host -v /etc/chains:/etc/chains -v /srv/chains:/srv/chains -v /dev/bus/usb:/dev/bus/usb -v /etc/localtime:/etc/localtime:ro chains/chains-master
```


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
