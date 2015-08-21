import usb.core
import usb.util

usb_iclass_map = {
    usb.CLASS_PER_INTERFACE: 'PerInterface',  # 0
    usb.CLASS_AUDIO: 'Audio',  # 1
    usb.CLASS_COMM: 'Comm',  # 2
    usb.CLASS_HID: 'HID',  # 3
    usb.CLASS_PRINTER: 'Printer',  # 7
    usb.CLASS_MASS_STORAGE: 'MassStorage',  # 8
    usb.CLASS_HUB: 'Hub',  # 9
    usb.CLASS_DATA: 'Data',
    usb.CLASS_VENDOR_SPEC: 'Vendor',
}

usb_iproto_map = {
    'PerInterface': {
    },
    'Audio': {
    },
    'Comm': {
    },
    'HID': {
        0: 'raw',
        1: 'keyboard',
        2: 'mouse',
    },
    'Printer': {
    },
    'MassStorage': {
    },
    'Hub': {
        0: 'full_speed',
    },
    'Data': {
    },
    'Vendor': {
    },
}

usb_services = {
    (0x16c0, 0x05df): [
        {'type': 'relay', 'name': 'usbrelay'},
    ],
    (0x045e, 0x028e): [
        {'type': 'joystick', 'name': 'xbox360'},
    ],
    (0x046d, 0xc21f): [
        {'type': 'joystick', 'name': 'f710'},  # Logitech F710 controller
    ],
    (0x08ff, 0x0009): [
        {'type': 'rfid', 'name': 'rfid_reader'},
    ],
}


def find_types(**kwargs):
    global usb_iclass_map
    global usb_iproto_map
    dev = usb.core.find(find_all=True, **kwargs)
    all_info = "All USB services:\n"
    types = {}
    dev_desc = {}
    for service in dev:
        #all_info += str(service) + '\n'
        for cindex, configuration in enumerate(service):
            # print 'Configuration: %d' % cindex
            for interface in configuration:
                # print interface.__dict__
                bclass = 'unknown'
                bproto = 'unknown'
                if interface.bInterfaceClass in usb_iclass_map:
                    bclass = usb_iclass_map[interface.bInterfaceClass]
                    if interface.bInterfaceProtocol in usb_iproto_map[bclass]:
                        bproto = usb_iproto_map[bclass][interface.bInterfaceProtocol]
                    #else:
                    #    bproto = 'unknown'
                dev_desc = {
                    'bus': service.bus,
                    'class': bclass,
                    'address': service.address,
                    'product_id': service.idProduct,
                    'vendor_id': service.idVendor,
                    'configuration': cindex,
                    'interface': interface.bInterfaceNumber
                }
                # Add service strings to interface description
                dev_desc.update(service_strings(service.bus, service.address))
                types.setdefault(bclass, {})
                # Adding interface to full list
                # print dev_desc
                types[bclass].setdefault(bproto, []).append(dev_desc)
    #print all_info
    return types


def service_strings(bus, address):
    """ Returns dictionary with service strings:

    usb_str = {
        'manufacturer_name': 'unknown',
        'product_name': 'unknown',
        'serialnumber': 'unkmown',
    }
    """
    dev = usb.core.find(bus=bus, address=address)
    usb_str = {
        'manufacturer_name': 'unknown',
        'product_name': 'unknown',
        'serialnumber': 'unkmown',
    }
    try:
        if dev._manufacturer is None:
            dev._manufacturer = usb.util.get_string(dev, dev.iManufacturer)
            usb_str['manufacturer_name'] = dev._manufacturer
        if dev._product is None:
            dev._product = usb.util.get_string(dev, dev.iProduct)
            usb_str['product_name'] = dev._product
        if dev._serial_number is None:
            dev._serial_number = usb.util.get_string(dev, dev.iSerialNumber)
            usb_str['serialnumber'] = dev._serial_number
    except:
        pass
    return usb_str


def find_mouse(**kwargs):
    types = find_types(**kwargs)
    if 'HID' in types:
        if 'mouse' in types['HID']:
            return types['HID']['mouse']
    return False


def find_keyboard(**kwargs):
    types = find_types(**kwargs)
    if 'HID' in types:
        if 'keyboard' in types['HID']:
            return types['HID']['keyboard']
    return False


def find_relay(**kwargs):
    types = find_types(**kwargs)
    if 'HID' in types:
        if 'relay' in types['HID']:
            return types['HID']['relay']
    return False


def find_joystick(**kwargs):
    types = find_types(**kwargs)
    if 'HID' in types:
        if 'joystick' in types['HID']:
            return types['HID']['joystick']
    return False

if __name__ == '__main__':
    from pprint import pprint
    import sys
    # in_img = sys.argv[1]
    # act = sys.argv[2]
    pprint(find_types())
    pprint(find_mouse())

