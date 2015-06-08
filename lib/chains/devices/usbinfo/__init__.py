#!/usr/bin/python2
import chains.device
from chains.common import log
from chains.common import cusb
import usb.core
import usb.util
import time


class USBInfoDevice(chains.device.Device):

    def onInit(self):
        # ## Device config
        self.interval = self.config.getInt('interval') or 600

    def onStart(self):
        while not self._shutdown:
            devs = self._get_all_devices()
            self._send_usbtree(devs)
            self._send_all_devices(devs)
            time.sleep(self.interval)

    def action_update_device(self, bus, address):
        '''
        Update information on specific usb device bus / address
        @param  bus  int  Bus number
        @param  address  int  Address number
        '''
        log.info('Running action_update_device')
        self._get_dev_path(bus, address)

    def _send_usbtree(self, usbtree):
        log.info('Running _send_usbtree')
        self.sendEvent('usb_tree', usbtree)

    def _send_all_devices(self, usbtree):
        log.info('Running _send_all_devices')
        for devkey in usbtree:
            self.sendEvent(devkey, usbtree[devkey])

    def _send_device(self, bus, address):
        log.info('Running _send_device')
        dev = self._get_dev_path(bus, address)
        devkey = "%03d:%03d" % (bus, address)
        self.sendEvent(devkey, dev)

    def _get_all_devices(self):
        log.info('Running _get_all_devices')
        # We only support 1 configuration, mulitple configurations are said to very rare
        # This saves us from a one level deeper dict which is unnecessary in most cases
        data = {}
        self.usb_devs = usb.core.find(find_all=True)
        for dev in self.usb_devs:
            devdict = self._get_device(dev)
            data.update(devdict)
        return data

    def _get_device(self, dev):
        log.info('Running _get_device')
        devdict = {}
        devkey = "%03d:%03d" % (dev.bus, dev.address)
        devdict.update({devkey: {
            'bLength': dev.bLength,
            'bDescriptorType': dev.bDescriptorType,
            'bcdUSB': dev.bcdUSB,
            'bDeviceClass': dev.bDeviceClass,
            'bDeviceSubClass': dev.bDeviceSubClass,
            'bDeviceProtocol': dev.bDeviceProtocol,
            'bMaxPacketSize0': dev.bMaxPacketSize0,
            'idVendor': dev.idVendor,
            'idProduct': dev.idProduct,
            'bcdDevice': dev.bcdDevice,
            'iManufacturer': dev.iManufacturer,
            'iProduct': dev.iProduct,
            'iSerialNumber': dev.iSerialNumber,
            'bNumConfigurations': dev.bNumConfigurations,
        }})
        devconf = {
            'conf': {
                'bLength': dev[0].bLength,
                'bDescriptorType': dev[0].bDescriptorType,
                'wTotalLength': dev[0].wTotalLength,
                'bNumInterfaces': dev[0].bNumInterfaces,
                'bConfigurationValue': dev[0].bConfigurationValue,
                'bmAttributes': dev[0].bmAttributes,
                'bMaxPower': dev[0].bMaxPower
            }
        }
        devdict[devkey].update(devconf)
        usb_strings = cusb.device_strings(dev)
        devdict[devkey].update(usb_strings)
        # dev[0] since we only check first configuration
        devdict[devkey].update({'interfaces': self._get_all_interfaces(dev[0])})
        return devdict

    def _get_all_interfaces(self, dev):
        log.info('Running _get_all_interfaces')
        data = {}
        for inter in dev:
            data.update(self._get_interface(inter))
        return data

    def _get_interface(self, inter):
        log.info('Running _get_interface')
        iface = {
            str(inter.bInterfaceNumber): {
                'bLength': inter.bLength,
                'bDescriptorType': inter.bDescriptorType,
                'bInterfaceNumber': inter.bInterfaceNumber,
                'bAlternateSetting': inter.bAlternateSetting,
                'bNumEndpoints': inter.bNumEndpoints,
                'bInterfaceClass': inter.bInterfaceClass,
                'bInterfaceSubClass': inter.bInterfaceSubClass,
                'bInterfaceProtocol': inter.bInterfaceProtocol,
                'iInterface': inter.iInterface,
            }
        }
        iface.update({'endpoints': self._get_all_endpoints(inter)})
        return iface

    def _get_all_endpoints(self, inter):
        log.info('Running _get_all_endpoints')
        data = {}
        for endpoint in inter:
            data.update(self._get_endpoint(endpoint))
        return data

    def _get_endpoint(self, endp):
        log.info('Running _get_endpoint')
        endpoint = {
            str(endp.bEndpointAddress): {
                'bLength': endp.bLength,
                'bDescriptorType': endp.bDescriptorType,
                'bEndpointAddress': endp.bEndpointAddress,
                'bmAttributes': endp.bmAttributes,
                'wMaxPacketSize': endp.wMaxPacketSize,
                'bInterval': endp.bInterval,
            }
        }
        return endpoint

    def _get_dev_path(self, bus, address):
        log.info('Running _get_dev_path')
        devkey = "%03d:%03d" % (bus, address)
        devs = self._get_all_devices()
        return devs[devkey]
