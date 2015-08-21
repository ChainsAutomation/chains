MODELS = [
    "bdm4065uc",
]

COMMANDS = [
    ['Get Platform and Version Labels', 'Request the SICP version', 0xA2,
        [
            (  # DATA[1] goes  here
                ('Get SICP implementation version', 0x00, {}),
                ('Get the software label and version information of the platform', 0x01, {}),
            ),
        ],
    ],
    ['Get Power State', 'Command requests the display to report its current power state', 0x19,
        [],
    ],
    ['Set Power State', 'Command to change the Power state of the display', 0x18,
        [
            (  # DATA[1] goes here
                ('Standby', 0x01, {}),
                ('On', 0x02, {}),
                ('Active-Off', 0x03, {}),
            ),
        ],
    ],
    ['Get User Input Control', 'Get the lock/unlock state', 0x1D,
        [
        ],
    ],
    ['Set User Input Control', 'Set the lock/unlock state', 0x1C,
        [
            (  # DATA[1] goes  here
                ('Remote Control Locked', 0x00, {}),
                ('Remote Control Unlocked', 0x01, {}),
                ('Local Keyboard Unlocked', 0x02, {}),
                ('Local Keyboard Locked', 0x03, {}),
            ),
        ],
    ],
    ['Get Power at Cold Start', 'Get Power state at Cold Start state', 0xA4,
        [
        ],
    ],
    ['Set Power at Cold Start', 'Set Power state at Cold Start', 0xA3,
        [
            (  # DATA[1] goes  here
                ('Power Off', 0x00, {}),
                ('Forced on', 0x01, {}),
                ('Last status', 0x02, {}),
            ),
        ],
    ],
    ['Set Input Source', 'Command requests the display to set the current input source', 0xAC,
        [
            (  # DATA[1] goes  here
                ('AV - Input Source Type', 0x01, {}),
                ('Card AV - Input Source Type', 0x01, {}),
                ('CVI 1 - Input Source Type', 0x03, {}),
                ('CVI 2 - Input Source Type', 0x03, {}),
                ('VGA - Input Source Type', 0x05, {}),
                ('HDMI (1) - Input Source Type', 0x09, {}),
                ('HDMI 2 - Input Source Type', 0x09, {}),
            ),
            (  # DATA[2] goes here
                ('AV - Input Source Number', 0x00, {}),
                ('Card AV - Input Source Number', 0x01, {}),
                ('CVI 1 - Input Source Number', 0x00, {}),
                ('CVI 2 - Input Source Number', 0x01, {}),
                ('VGA - Input Source Number', 0x00, {}),
                ('HDMI (1) - Input Source Number', 0x00, {}),
                ('HDMI 2 - Input Source Number', 0x01, {}),
            ),
            (  # DATA[3] goes here
                ('OSD Style', 0x01, {}),
            ),
            (  # DATA[3] goes here
                ('Mute Style', 0x00, {}),
            ),
        ],
    ],
    ['Get Current Source', 'Command requests the display to report the current input source in use.', 0xAD,
        [
        ],
    ],
    ['Get Video Paramters', 'Command requests the display to report its current video parameters.', 0x33,
        [
        ],
    ],
    ['Set Video Paramters', 'Command sets the video parameters.', 0x32,
        [
            (  # DATA[1] goes  here
                ('Brightness: 0-100%', 0x00, {'type': 'range', 'min': 0, 'max': 100, 'data': 'hex'}),
            ),
            (  # DATA[1] goes  here
                ('Color: 0-100%', 0x00, {'type': 'range', 'min': 0, 'max': 100, 'data': 'hex'}),
            ),
            (  # DATA[1] goes  here
                ('Contrast: 0-100%', 0x00, {'type': 'range', 'min': 0, 'max': 100, 'data': 'hex'}),
            ),
            (  # DATA[1] goes  here
                ('Sharpness: 0-100%', 0x00, {'type': 'range', 'min': 0, 'max': 100, 'data': 'hex'}),
            ),
            (  # DATA[1] goes  here
                ('Tint/Hue: 0-100%', 0x00, {'type': 'range', 'min': 0, 'max': 100, 'data': 'hex'}),
            ),
        ],
    ],
    ['Get Picture Format', 'Command requests the display to report its current picture format', 0x3B,
        [
        ],
    ],
    # TODO: This limits us to 16:9 screen, different values for other aspect ratios
    ['Set Picture Format', 'Command requests the display to set the specified picture format', 0x3A,
        [
            (  # DATA[1] goes  here
                ('Normal - picture format (16:9)', 0x00, {}),
                ('Custom - picture format (16:9)', 0x01, {}),
                ('Real - picture format (16:9)', 0x02, {}),
                ('Full - picture format (16:9)', 0x03, {}),
            ),
        ],
    ],
    ['Set Picture-in-Picture (PIP)', 'Command requests the display to set the specified PIP settings.', 0x3C,
        [
            (  # DATA[1] goes  here
                ('PIP off', 0x00, {}),
                ('PIP on', 0x01, {}),
            ),
            (  # DATA[1] goes  here
                ('PIP position 00 (typically bottom-left)', 0x00, {}),
                ('PIP position 01 (typically top-left)', 0x01, {}),
                ('PIP position 10 (typically top-right)', 0x02, {}),
                ('PIP position 11 (typically bottom-right)', 0x03, {}),
            ),
            (  # DATA[1] goes  here
                ('Reserved', 0x00, {}),
            ),
            (  # DATA[1] goes  here
                ('Reserved', 0x00, {}),
            ),
        ],
    ],
    ['Set PIP Source', 'Command requests the display to set the specigfied PIP source.', 0x84,
        [
            (  # DATA[1] goes  here
                ('Input Source (normal state)', 0xFD, {}),
                ('Reserved for smartcard', 0xFE, {}),
            ),
            (  # DATA[1] goes  here
                ('AV - source number', 0x01, {}),
                ('VIDEO - source number', 0x03, {}),
                ('CVI - source number', 0x06, {}),
                ('VGA - source number', 0x08, {}),
                ('HDMI - source number', 0x0A, {}),
                ('HDMI 2 - source number', 0x0B, {}),
            ),
        ],
    ],
    ['Get Audio Parameters', 'Command requests the display to report its current audio parameters', 0x43,
        [
        ],
    ],
    ['Set Audio Parameters', 'Command to change the audio parameters on the display.', 0x42,
        [
            (  # DATA[1] goes  here
                ('Treble (0-100)%', 0x00, {'type': 'range', 'min': 0, 'max': 100, 'data': 'hex'}),
                ('Bass (0-100)%', 0x00, {'type': 'range', 'min': 0, 'max': 100, 'data': 'hex'}),
            ),
        ],
    ],
    ['Get Audio Volume', 'Command requests the display to report its current Volume level', 0x45,
        [
        ],
    ],
    ['Set Audio Volume', 'Command requests the display to set its current Volume level', 0x44,
        [
            (  # DATA[1] goes  here
                ('Volume level (0-100)%', 0x00, {'type':'range', 'min': 0, 'max': 100}),
            ),
        ],
    ],
    ['Get Misc Info', 'Command requests the display to report from miscellaneous information parameters', 0x0F,
        [
            (  # DATA[1] goes  here
                ('Operating hours', 0x02, {}),
            ),
        ],
    ],
    ['Set Smart Power', 'Command requests the display to set the specified Power Saving Mode.', 0xDD,
        [
            (  # DATA[1] goes  here
                ('Off (no special action, default mode)', 0x00, {}),
                ('Low (same as off)', 0x01, {}),
                ('Medium', 0x02, {}),
                ('High (Highest power saving mode)', 0x03, {}),
            ),
        ],
    ],
    ['Set Video Alignment', 'Command requests the display to make auto adjustment on VGA input source.', 0x70,
        [
            (  # DATA[1] goes  here
                ('Auto Adjust', 0x40, {}),
            ),
            (  # DATA[2] goes  here
                ('Static value', 0x00, {}),
            ),
        ],
    ],
    ['Get temperature Sensor', 'Command requests the display to report its value of the temperature sensors (±3°C).', 0x2F,
        [
        ],
    ],
    ['Get Serial Code', 'Command requests the display to report its Serial Code Number (Production code) 14 digits', 0x15,
        [
        ],
    ],
]
