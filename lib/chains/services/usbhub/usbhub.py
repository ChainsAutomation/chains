import sys
import usb

# Stuff pulled from usb-ctrl.py
# unfortunately it no longer works with the new pyusb
# Testing it out in the __name__ == __main__ section

USB_RT_HUB              =       (usb.TYPE_CLASS | usb.RECIP_DEVICE)
USB_RT_PORT             =       (usb.TYPE_CLASS | usb.RECIP_OTHER)
USB_PORT_FEAT_RESET     =       4
USB_PORT_FEAT_POWER     =       8
USB_PORT_FEAT_INDICATOR =       22
USB_DIR_IN              =       0x80             # service to host

COMMAND_SET_NONE  = 0
COMMAND_SET_LED   = 1
COMMAND_SET_POWER = 2

HUB_LED_GREEN     = 2


if __name__ == '__main__':
    bus = int(sys.argv[1])
    address = int(sys.argv[2])
    print "opening bus=%d,address=%d" % (bus, address)

    dev = usb.core.find(bus=bus,address=address)

    # uh = dev.open()

    desc = None

    # the below needs to be changed to the new pyusb library
    desc = dev.controlMsg(requestType = USB_DIR_IN | USB_RT_HUB,
                         request = usb.REQ_GET_DESCRIPTOR,
                         value = usb.DT_HUB << 8,
                         index = 0, buffer = 1024, timeout = 1000
                         )
    print "Hub has %d ports" % desc[2]
    hub_ports = desc[2]

    # desc[3] is lower byte of wHubCharacteristics
    if (desc[3] & 0x80) == 0 and (desc[3] & 0x03) >= 2:
        sys.exit("Hub doesn't have features of controling port power/indicator")
    else:
        print "Hub has power control features!"

    if (desc[3] & 0x03) == 0:
        print " INFO: ganged power switching."
    elif (desc[3] & 0x03) == 1:
        print " INFO: individual power switching."
    elif (desc[3] & 0x03) == 2 or (desc[3] & 0x03) == 3:
        print " WARN: no power switching."
    if (desc[3] & 0x80) == 0:
        print " WARN: Port indicators are NOT supported."

    print " Hub Port Status:"
    for i in range(hub_ports):
        port = i + 1
        status = handle.controlMsg(requestType = USB_RT_PORT | usb.ENDPOINT_IN,
                                   request = usb.REQ_GET_STATUS,
                                   value = 0,
                                   index = port, buffer = 4,
                                   timeout = 1000)

        print "   Port %d: %02x%02x.%02x%02x" % (port, status[3], status[2],
                                                 status[1], status[0]),
        if status[1] & 0x10:
            print " indicator",
        if status[1] & 0x08:
            print " test" ,
        if status[1] & 0x04:
            print " highspeed",
        if status[1] & 0x02:
            print " lowspeed",
        if status[1] & 0x01:
            print " power",

        if status[0] & 0x10:
            print " RESET",
        if status[0] & 0x08:
            print " oc",
        if status[0] & 0x04:
            print " suspend",
        if status[0] & 0x02:
            print " enable",
        if status[0] & 0x01:
            print " connect",

        print

