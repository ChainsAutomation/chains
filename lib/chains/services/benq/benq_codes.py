<<<<<<< HEAD
=======
## rs232 codes
# Format:
# "<CR>*command=parameter#<CR>"
## Examples
# power on: <CR>*pow=on#<CR>
# power off: <CR>*pow=off#<CR>
# power status: <CR>*pow=?#<CR>


TOPICS = [
            ['pow', 'Power Commands'],
            ['sour', 'Source Selection'],
            ['mute', 'Mute Commands'],
            ['vol', 'Volume Commands'],
            ['micvol', 'Microphone Commands'],
            ['audiosour', 'Audio Source Selection'],
            ['appmod', 'Picture Mode'],
            ['con', 'Contrast'],
            ['bri', 'Brightness'],
            ['color', 'Color'],
            ['sharp', 'Sharpness'],
            ['ct', 'Color Temperature'],
            ['asp', 'Aspect Ratio'],
            ['zoom', 'Digital Zoom'],
            ['auto', 'Auto'],
            ['BC', 'Brilliant Color'],
            ['pp', 'Projector Position'],
            ['QAS', 'Quick Auto Search'],
            ['directpower', 'Direct Power On'],
            ['autopower', 'Signal Power On'],
            ['standbynet', 'Standby Settings Network'],
            ['standbymic', 'Standby Settings Microphone'],
            ['standbymnt', 'Standby Settings Monitor'],
            ['baud', 'Baud Rate'],
            ['ltim', 'Lamp Hour'],
            ['ltim2', 'Lamp2 Hour'],
            ['lampm', 'Lamp Mode'],
            ['modelname', 'modelname'],
            ['blank', 'Blank Settings'],
            ['freeze', 'Freeze Settings'],
            ['menu', 'Menu'],
            ['up', 'Menu Up'],
            ['down', 'Menu Down'],
            ['left', 'Menu Left'],
            ['right', 'Menu Right'],
            ['enter', 'Menu Enter'],
            ['3d', '3D Settings'],
            ['rr', 'Remote Receiver'],
            ['ins', 'Instant On'],
            ['lpsaver', 'Lamp Saver Mode'],
            ['prjlogincode', 'Projector Login Code'],
            ['broadcasting', 'Broadcasting'],
            ['amxdd', 'AMX Service Discovery'],
            ['macaddr', 'MAC Address'],
            ['Highaltitude', 'High Altitude Mode'],
]

>>>>>>> 589d1783873b05cac1b992b3b1604ce9e72b3f5c

MODELS = [
        'W6000',
        'W6500',
]

<<<<<<< HEAD



CMDS = [
    ["pow", "System Power Command", [
        ["on", "Power on", {}, ],
        ["off", "Power off", {}, ],
        ["?", "Get Power Status", {}, ],
    ]],
    ["sour", "Source Selection", [
        ["RGB", "COMPSTER/YPbPr", {}, ],
        ["RGB2", "COMPUTER 2/YPbPr2", {}, ],
        ["ypbr", "Component", {}, ],
        ["dviA", "DVI-A", {}, ],
        ["dvid", "DVI-D", {}, ],
        ["hdmi", "HDMI", {}, ],
        ["hdmi2", "HDMI 2", {}, ],
        ["vid", "Composite", {}, ],
        ["svid", "S-Video", {}, ],
        ["network", "Network", {}, ],
        ["usbdisplay", "USB Display", {}, ],
        ["usbreader", "USB Reaer", {}, ],
        ["?", "Get Current source", {}, ],
    ]],
    ["mute", "Mute Command", [
        ["on", "Mute on", {}, ],
        ["off", "Mute off", {}, ],
        ["?", "Get Mute Status", {}, ],
    ]],

]
=======
CMDS = {
        'pow': {},
        'sour': {},
        'mute': {},
        'vol': {},
        'micvol': {},
        'audiosour': {},
        'appmod': {},
        'con': {},
        'bri': {},
        'color': {},
        'sharp': {},
        'ct': {},
        'asp': {},
        'zoom': {},
        'auto': {},
        'BC': {},
        'pp': {},
        'QAS': {},
        'directpower': {},
        'autopower': {},
        'standbynet': {},
        'standbymic': {},
        'standbymnt': {},
        'baud': {},
        'ltim': {},
        'ltim2': {},
        'lampm': {},
        'modelname': {},
        'blank': {},
        'freeze': {},
        'menu': {},
        'up': {},
        'down': {},
        'left': {},
        'right': {},
        'enter': {},
        '3d': {},
        'rr': {},
        'ins': {},
        'lpsaver': {},
        'prjlogincode': {},
        'broadcasting': {},
        'amxdd': {},
        'macaddr': {},
        'Highaltitude': {},
}

>>>>>>> 589d1783873b05cac1b992b3b1604ce9e72b3f5c
