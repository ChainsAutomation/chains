
MODELS = [
        'W6000',
        'W6500',
]




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
