CMD = {
    0xA2: {'desc': 'Platform and Version Labels - Get',
        0x00: 'Get SICP implementation version',
        0x01: 'Get the software label and version information of the platform ',
    }
}

GET_CMDS = {
    'Get platform and version labels': [
        (0xA2, 'Request the SICP version'),
        (
            (0x00, 'Get SICP implementation version'),
            (0x01, 'Get software label')
        ),
    ]
}
