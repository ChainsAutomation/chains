MODELS = [
    "bdl4221",
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
                ('Power off', 0x01, {}),
                ('Power on', 0x02, {}),
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
    ['Get User Input Control State', 'Get the lock/unlock state for All/Voume/Power', 0x1B,
        [
        ],
    ],
    ['Set User Input Control State', 'Set the lock/unlock state for All/Voume/Power', 0x1A,
        [
            (  # DATA[1] goes  here
                ('Remote Lock all', 0x01, {}),
                ('Remote Lock all but volume', 0x02, {}),
                ('Remote Lock all but power', 0x03, {}),
            ),
            (  # DATA[2] goes  here
                ('Keyboard Lock all', 0x01, {}),
                ('Keyboard Lock all but volume', 0x02, {}),
                ('Keyboard Lock all but power', 0x03, {}),
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
                ('VIDEO - Input Source Type', 0x01, {}),
                ('S-VIDEO - Input Source Type', 0x01, {}),
                ('COMPONENT - Input Source Type', 0x03, {}),
                ('CVI2 - Input Source Type', 0x03, {}),
                ('VGA - Input Source Type', 0x05, {}),
                ('HDMI2 - Input Source Type', 0x05, {}),
                ('Display Port 2 - Input Source Type', 0x06, {}),
                ('USB 2 - Input Source Type', 0x06, {}),
                ('Card DVI-D - Input Source Type', 0x07, {}),
                ('Display Port 1 - Input Source Type', 0x07, {}),
                ('Card OPS - Input Source Type', 0x08, {}),
                ('USB (1) - Input Source Type', 0x08, {}),
                ('HDMI or HDMI 1 - Input Source Type', 0x09, {}),
                ('DVI-D - Input Source Type', 0x09, {}),
            ),
            (  # DATA[2] goes here
                ('VIDEO - Input Source Number', 0x00, {}),
                ('S-VIDEO - Input Source Number', 0x01, {}),
                ('COMPONENT - Input Source Number', 0x00, {}),
                ('CVI 2 - Input Source Number', 0x01, {}),
                ('VGA - Input Source Number', 0x00, {}),
                ('HDMI 2 - Input Source Number', 0x01, {}),
                ('HDMI (1) - Input Source Number', 0x00, {}),
                ('DVI-D - Input Source Number', 0x01, {}),
                ('Card DVI-D - Input Source Number', 0x00, {}),
                ('Display Port (1) - Input Source Number', 0x01, {}),
                ('Card OPS - Input Source Number', 0x00, {}),
                ('USB (1) - Input Source Number', 0x01, {}),
                ('USB 2 - Input Source Number', 0x00, {}),
                ('Display Port 2 - Input Source Number', 0x01, {}),
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
    ['Get Auto Signal Detection', 'Command requests the display to report its current Auto Signal Detecting status', 0xAF,
        [
        ],
    ],
    ['Set Auto Signal Detection', 'Command to change the current Auto Signal Detection setting', 0xAE,
        [
            (  # DATA[1] goes  here
                ('Off', 0x00, {}),
                ('On', 0x01, {}),
            ),
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
    ['Get Color Temperature', 'Command requests the display to report its current color temperature.', 0x35,
        [
        ],
    ],
    ['Set Color Temperature', 'Command requests the display to report its current color temperature.', 0x34,
        [
            (  # DATA[1] goes  here
                ('User', 0x00, {}),
                ('Nature', 0x01, {}),
                ('11000K', 0x02, {}),
                ('10000K', 0x03, {}),
                ('9300K', 0x04, {}),
                ('7500K', 0x05, {}),
                ('6500K', 0x06, {}),
                ('5770K', 0x07, {}),
                ('5500K', 0x08, {}),
                ('5000K', 0x09, {}),
                ('4000K', 0x0A, {}),
                ('3400K', 0x0B, {}),
                ('3350K', 0x0C, {}),
                ('3000K', 0x0D, {}),
                ('2800K', 0x0E, {}),
                ('2600K', 0x0F, {}),
                ('1850K', 0x10, {}),
            ),
        ],
    ],
    ['Get Color Parameters', 'Command requests the display to report its current color parameters.', 0x37,
        [
        ],
    ],
    ['Set Color Parameters', 'Command to change the current color parameters', 0x36,
        [
            (  # DATA[1] goes  here
                ('Red color gain value', 0x00, {'type': 'range', 'min': 0, 'max': 255, 'data': 'hex'}),
            ),
            (  # DATA[1] goes  here
                ('Green color gain value', 0x00, {'type': 'range', 'min': 0, 'max': 255, 'data': 'hex'}),
            ),
            (  # DATA[1] goes  here
                ('Blue color gain value', 0x00, {'type': 'range', 'min': 0, 'max': 255, 'data': 'hex'}),
            ),
            (  # DATA[1] goes  here
                ('Red color offset value', 0x00, {'type': 'range', 'min': 0, 'max': 255, 'data': 'hex'}),
            ),
            (  # DATA[1] goes  here
                ('Green color offset value', 0x00, {'type': 'range', 'min': 0, 'max': 255, 'data': 'hex'}),
            ),
            (  # DATA[1] goes  here
                ('Blue color offset value', 0x00, {'type': 'range', 'min': 0, 'max': 255, 'data': 'hex'}),
            ),
        ],
    ],
    ['Get Picture Format', 'Command requests the display to report its current picture format', 0x3B,
        [
        ],
    ],
    ['Set Picture Format', 'Command requests the display to set the specified picture format', 0x3A,
        [
            (  # DATA[1] goes  here
                ('Normal - picture format', 0x00, {}),
                ('Custom - picture format', 0x01, {}),
                ('Real - picture format', 0x02, {}),
                ('Full - picture format', 0x03, {}),
                ('21:9 - picture format', 0x04, {}),
                ('Dynamic - picture format', 0x05, {}),
            ),
        ],
    ],
    ['Get Picture-in-Picture (PIP)', 'Command requests the display to get the specified PIP settings.', 0x3D,
        [
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
    ['Get PIP Source', 'Command requests the display to report its current PIP source setting.', 0x85,
        [
        ],
    ],
    ['Set PIP Source', 'Command requests the display to set the specigfied PIP source.', 0x84,
        [
            (  # DATA[1] goes  here
                ('Input Source (normal state)', 0xFD, {}),
                ('Reserved for smartcard', 0xFE, {}),
            ),
            (  # DATA[1] goes  here
                ('VIDEO - source number', 0x01, {}),
                ('S-VIDEO - source number', 0x03, {}),
                ('COMPONENT - source number', 0x06, {}),
                ('VGA - source number', 0x08, {}),
                ('HDMI 2 - source number', 0x09, {}),
                ('HDMI (1) - source number', 0x0A, {}),
                ('DVI-D - source number', 0x0B, {}),
                ('Card DVI-D - source number', 0x0C, {}),
                ('Display Port (1) - source number', 0x0D, {}),
                ('Card OPS - source number', 0x0E, {}),
                ('USB (1) - source number', 0x0F, {}),
                ('USB 2 - source number', 0x10, {}),
                ('Display Port 2 - source number', 0x11, {}),
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
    ['Set Audio Volume Limits', 'Command requests the display to set its current Volume Limit level', 0xB8,
        [
            (  # DATA[1] goes  here
                ('Minimum Volume (0-100)%', 0x00, {'type': 'range', 'min': 0, 'max': 100}),
            ),
            (  # DATA[1] goes  here
                ('Maximum Volume (0-100)%', 0x00, {'type': 'range', 'min': 0, 'max': 100}),
            ),
            (  # DATA[1] goes  here
                ('Switch on Volume (0-100)%', 0x00, {'type': 'range', 'min': 0, 'max': 100}),
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
    ['Get Misc Info', 'Command requests the display to report from miscellaneous information parameters', 0x0F,
        [
            (  # DATA[1] goes  here
                ('Operating hours', 0x02, {}),
            ),
        ],
    ],
    ['Get Smart Power', 'Command requests the display to get the specified Power Saving Mode.', 0xDE,
        [
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
    ['Get Tiling', 'Command requests the display to report Tiling status.', 0x23,
        [
        ],
    ],
    ['Set Tiling', 'Command sets the Tiling settings.', 0x22,
        [
            (  # DATA[1] goes  here
                ('Disable', 0x00, {}),
                ('Enable', 0x01, {}),
            ),
            (  # DATA[1] goes  here
                ('Frame comp: No', 0x00, {}),
                ('Frame comp: Yes', 0x01, {}),
                ('Frame comp: Don\'t overwrite', 0x02, {}),
            ),
            (  # DATA[1] goes  here
                ('Position', 0x00, {'type': 'range', 'min': 0, 'max': 255, 'data': 'hex'}),
            ),
            (  # DATA[1] goes  here
                ## TODO: doc h/v monitor logic
                ('V Monitors, H Monitors (0: no change)', 0x00, {'type': 'range', 'min': 0, 'max': 255, 'data': 'hex'}),
            ),
        ],
    ],
    ['Get Light Sensor', 'Command requests the display to report its current light sensor status.', 0x25,
        [
        ],
    ],
    ['Set Light Sensor', 'Command to change the light sensor setting of the display.', 0x24,
        [
            (  # DATA[1] goes  here
                ('Off', 0x00, {}),
                ('On', 0x01, {}),
            ),
        ],
    ],
    ['Get OSD Rotation', 'Command requests the display to report its current OSD rotation status', 0x27,
        [
        ],
    ],
    ['Set OSD Rotation', 'Command requests the display to set the OSD rotation', 0x26,
        [
            (  # DATA[1] goes  here
                ('Off', 0x00, {}),
                ('On', 0x01, {}),
            ),
        ],
    ],
    ['Get MEMC Effect', 'Command requests the display to report its current MEMC effect status', 0x29,
        [
        ],
    ],
    ['Get MEMC Effect', 'Command requests the display to report its current MEMC effect status', 0x28,
        [
            (  # DATA[1] goes  here
                ('Off', 0x00, {}),
                ('Low', 0x01, {}),
                ('Medium', 0x02, {}),
                ('High', 0x03, {}),
            ),
        ],
    ],
    ['Get Touch Feature', 'Command requests the display to report its current Touch Feature status', 0x1F,
        [
        ],
    ],
    ['Set Touch Feature', 'Command sets the Touch Feature', 0x1E,
        [
            (  # DATA[1] goes  here
                ('Off', 0x00, {}),
                ('On', 0x01, {}),
            ),
        ],
    ],
]  # End of COMMANDS array

