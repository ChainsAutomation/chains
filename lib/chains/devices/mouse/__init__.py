#!/usr/bin/python2
import chains.device
from chains.common import log
from chains.common import usb as cusb
import sys
import usb.core
import usb.util
from array import array
# from datetime import datetime, timedelta


class MouseDevice(chains.device.Device):

    def onInit(self):
        self.button_events = [
            array('B', [1, 0, 0, 0, 0, 0, 0]), 'button_release',
            array('B', [1, 1, 0, 0, 0, 0, 0]), 'button_left',
            array('B', [1, 2, 0, 0, 0, 0, 0]), 'button_right',
            array('B', [1, 4, 0, 0, 0, 0, 0]), 'button_middle',
            array('B', [1, 8, 0, 0, 0, 0, 0]), 'button_3',
            array('B', [1, 16, 0, 0, 0, 0, 0]), 'button_4',
            array('B', [1, 32, 0, 0, 0, 0, 0]), 'button_5',
            array('B', [1, 64, 0, 0, 0, 0, 0]), 'button_6',
            array('B', [1, 128, 0, 0, 0, 0, 0]), 'button_7',
            array('B', [1, 255, 0, 0, 0, 0, 0]), 'button_8',
            array('B', [1, 0, 0, 0, 0, 0, 1]), 'wheel_up',
            array('B', [1, 0, 0, 0, 0, 0, 255]), 'wheel_down',
            # mouse button combinations
            # TODO: do this by using bitwise operator to generate all combinations
            array('B', [1, 3, 0, 0, 0, 0, 0]), 'button_left_right',
            array('B', [1, 5, 0, 0, 0, 0, 0]), 'button_left_middle',
            array('B', [1, 6, 0, 0, 0, 0, 0]), 'button_right_middle',
            array('B', [1, 7, 0, 0, 0, 0, 0]), 'button_left_right_middle',
        ]
        # "slow" mouse movements
        self.move_events = [
            array('B', [1, 0, 0, 0, 1, 0, 0]), 'down',
            array('B', [1, 0, 255, 255, 1, 0, 0]), 'down-left',
            array('B', [1, 0, 1, 0, 1, 0, 0]), 'down-right',
            array('B', [1, 0, 0, 0, 255, 255, 0]), 'up',
            array('B', [1, 0, 255, 255, 255, 255, 0]), 'up-left',
            array('B', [1, 0, 1, 0, 255, 255, 0]), 'up-right',
            array('B', [1, 0, 255, 255, 0, 0, 0]), 'left',
            array('B', [1, 0, 1, 0, 0, 0, 0]), 'right',
        ]
        # ## Device config
        self.interval = int(self.config.get('interval'))
        if not self.interval:
            self.interval = 600  # milliseconds
        self.vendorid = int(self.config.get('vendorid'))
        self.productid = int(self.config.get('productid'))
        self.search_params = {}
        if self.vendorid and self.productid:
            self.search_params.update({'idVendor': self.vendorid, 'idProduct': self.productid})
            mousedevs = cusb.find_mouse(self.search_params)
        else:
            mousedevs = cusb.find_mouse()
        if not mousedevs:
            log("Can't find mouse device")
            sys.exit("Can't find mouse device")
        # Use first matching mouse
        mouse = mousedevs[0]
        # ## vendor and product ids
        self.dev = usb.core.find(address=mouse['address'], bus=mouse['bus'])
        self.interface = mouse['interface']
        # use the first endpoint
        # dev[configuration][(interface, alt_config)][endpoint]
        self.endpoint = self.dev[mouse['configuration']][(mouse['interface'], 0)][0]

    def onStart(self):
        # move_start = False
        # moves = []
        if self.dev.is_kernel_driver_active(self.interface) is True:
            # detach from kernel if device is being used
            self.dev.detach_kernel_driver(self.interface)
            # claim the device
            usb.util.claim_interface(self.dev, self.interface)
        while not self._shutdown:
            try:
                data = self.dev.read(self.endpoint.bEndpointAddress, self.endpoint.wMaxPacketSize)
                try:
                    # print self.move_events[self.move_events.index(data) + 1]
                    mevent = self.move_events[self.move_events.index(data) + 1]
                    # if not move_start:
                    #    move_start = datetime.now()
                    # move.append(data)
                    self.sendEvent('move', {'direction': mevent})
                except ValueError:
                    try:
                        # print self.button_events[self.button_events.index(data) + 1]
                        mevent = self.button_events[self.button_events.index(data) + 1]
                        self.sendEvent('click', {'button': mevent})
                    except ValueError:
                        # TODO: support accelerated mouse movements
                        # Undefined event
                        # print data
                        # TODO: support aggregated movement
                        # if not move_start:
                        #    move_start = datetime.now()
                        # move.append(data)
                        pass
            except usb.core.USBError as e:
                data = None
                if e.args == ('Operation timed out',):
                    continue
            # TODO: support aggregated movement
            # if move_start + timedelta(milliseconds=self.interval) < datetime.now():
            #     direction = self.calc_agg_mov(moves)
            #     self.sendEvent('move_agg', {'direction': direction})
            #     move_start = False
            #     moves = []

    def onShutdown(self):
        # release the device
        usb.util.release_interface(self.dev, self.interface)
        # reattach the device to the kernel
        self.dev.attach_kernel_driver(self.interface)
