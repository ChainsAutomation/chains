from __future__ import absolute_import
import chains.service
from chains.common import log
import sys
import usb.core
import usb.util
from chains.common import cusb
from array import array
# from datetime import datetime, timedelta


class KeyboardService(chains.service.Service):

    def onInit(self):
        self.keymaps = {
            'en_US': [
                '', '', '', '',
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '\n', '^]', '^H',
                '^I', ' ', '-', '=', '[', ']', '\\', '>', ';', "'", '`', ',', '.',
                '/', 'CapsLock', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
                'PS', 'SL', 'Pause', 'Ins', 'Home', 'PU', '^D', 'End', 'PD', '->', '<-', '-v', '-^', 'NL',
                'KP/', 'KP*', 'KP-', 'KP+', 'KPE', 'KP1', 'KP2', 'KP3', 'KP4', 'KP5', 'KP6', 'KP7', 'KP8',
                'KP9', 'KP0', '\\', 'App', 'Pow', 'KP=', 'F13', 'F14'
            ]
        }

        self.shiftmaps = {
            'en_US': [
                '', '', '', '',
                'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '\n', '^]', '^H',
                '^I', ' ', '_', '+', '{', '}', '|', '<', ':', '"', '~', '<', '>',
                '?', 'CapsLock', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
                'PS', 'SL', 'Pause', 'Ins', 'Home', 'PU', '^D', 'End', 'PD', '->', '<-', '-v', '-^', 'NL',
                'KP/', 'KP*', 'KP-', 'KP+', 'KPE', 'KP1', 'KP2', 'KP3', 'KP4', 'KP5', 'KP6', 'KP7', 'KP8',
                'KP9', 'KP0', '|', 'App', 'Pow', 'KP=', 'F13', 'F14'
            ]
        }

        self.mods = {
            1: 'control_left',  # Left control
            2: 'shift_left',  # Left shift
            4: 'alt_left',  # Left alt
            8: 'super_left',  # Left super
            16: 'control_right',  # Right control
            32: 'shift_right',  # Right shift
            64: 'alt_right',  # Right alt
            128: 'super_right',  # Right super
        }
        # ## Service config
        self.interval = int(self.config.get('interval')) or 10
        self.max_word = int(self.config.get('max_word')) or 50
        self.max_line = int(self.config.get('max_line')) or 250
        self.vendorid = int(self.config.get('vendorid'))
        self.productid = int(self.config.get('productid'))

        self.search_params = {}
        if self.vendorid and self.productid:
            self.search_params.update({'idVendor': self.vendorid, 'idProduct': self.productid})
            kbdevs = cusb.find_keyboard(self.search_params)
        else:
            log.warn("No config, using first found usb keyboard")
            kbdevs = cusb.find_keyboard()
        if not kbdevs:
            log.error("Can't find keyboard")
            sys.exit("Can't find keyboard")
        # Use first matching keyboard
        keyboard = kbdevs[0]
        # ## vendor and product ids
        self.dev = usb.core.find(address=keyboard['address'], bus=keyboard['bus'])
        self.interface = keyboard['interface']
        # use the first endpoint
        # dev[configuration][(interface, alt_config)][endpoint]
        self.endpoint = self.dev[keyboard['configuration']][(keyboard['interface'], 0)][0]

    def onStart(self):
        # line_start = False
        # line = []
        if self.dev.is_kernel_driver_active(self.interface) is True:
            # detach from kernel if keyboard is being used
            self.dev.detach_kernel_driver(self.interface)
            # claim the keyboard
            usb.util.claim_interface(self.dev, self.interface)
        cur_state = array('B', [0, 0, 0, 0, 0, 0, 0, 0])
        cur_line = ""
        while not self._shutdown:
            try:
                data = self.dev.read(self.endpoint.bEndpointAddress, self.endpoint.wMaxPacketSize)
                if not cur_state == data:
                    key_stat = self.keychange(cur_state, data)
                    # print key_stat
                    cur_state = data
                    self.sendEvent(key_stat['keyevent'], key_stat)
                    # Check for special key presses (space, newline)
                    if key_stat['keyevent'] == 'click':
                        # Check for special key presses (space, newline)
                        if key_stat['keycode'] == 44 or key_stat['keycode'] == '40':  # space / newline
                            word = cur_line.rsplit(' ', 1)[0]
                            if word:
                                self.sendEvent('word', word[-self.max_word:])
                            if key_stat['keycode'] == 40:  # newline
                                self.sendEvent('line', cur_line[-self.max_line:])
                                cur_line = ""
                            if key_stat['keycode'] == '44':
                                cur_line += key_stat['active_key']
                        else:
                            cur_line += key_stat['active_key']
            except usb.core.USBError as e:
                data = None
                if e.args == ('Operation timed out',):
                    continue

    def onShutdown(self):
        # release the keyboard
        usb.util.release_interface(self.dev, self.interface)
        # reattach the keyboard to the kernel
        self.dev.attach_kernel_driver(self.interface)

    def _is_shifted(self, modflags):
        for val in self.mods:
            if self.mods[val].startswith('shift') and modflags & val:
                return True
        return False

    def _get_mods(self, modflags):
        ret_mods = []
        if modflags == 0:
            return []
        for val in self.mods:
            if modflags & val:
                ret_mods.append(self.mods[val])
        return ret_mods

    def keychange(self, cur, new, keymap='en_US'):
        keys_pressed = []
        mods_pressed = []
        # print "Old data: %s" % str(cur)
        # print "New data: %s" % str(new)
        for index, value in enumerate(new):
            # print "Comparing %d indexes" % index
            # print "cur: %d -- new: %d" % (cur[index], new[index])
            if value != cur[index]:  # key change
                if (index == 0 and cur[index] > value) or value == 0:
                    keyevent = 'release'
                else:
                    keyevent = 'click'
                if index == 0:  # Change to modifiers
                    if cur[index] < value:  # modifier pressed
                        akey = self.mods[value - cur[index]]
                        keycode = value
                        # print "Mod pressed: %s" % self.mods[value - cur[index]]
                    else:  # modifier released
                        keycode = cur[index]
                        akey = self.mods[cur[index] - value]
                        # print "Mod released: %s" % self.mods[cur[index] - value]
                else:  # Change to regular keys
                    # print "value in %d changed from %d to %d" % (index, cur[index], new[index])
                    if value == 0:  # key released
                        # keyevent = 'release'
                        keycode = cur[index]
                        # print "Key released: %d" % cur[index]
                        if not self._is_shifted(new[0]):
                            akey = self.keymaps[keymap][keycode]
                        else:
                            akey = self.shiftmaps[keymap][keycode]
                    else:  # Key pressed
                        # print "Key pressed: %d" % value
                        keycode = value
                        if not self._is_shifted(new[0]):
                            akey = self.keymaps[keymap][keycode]
                            keys_pressed.append(self.keymaps[keymap][keycode])
                        else:
                            akey = self.shiftmaps[keymap][keycode]
                            keys_pressed.append(self.shiftmaps[keymap][keycode])
            else:
                # unchanged value
                if not index == 0 and not value == 0:
                    if not self._is_shifted(new[0]):
                        keys_pressed.append(self.keymaps[keymap][value])
                    else:
                        keys_pressed.append(self.shiftmaps[keymap][value])
        mods_pressed = self._get_mods(new[0])
        return {'keyevent': keyevent, 'active_key': akey, 'keys': keys_pressed, 'mods': mods_pressed, 'keycode': keycode}
