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

CMDS = [
    ['Command Name', 'Command Desc', 'Command Value (hex)',
        [
            (  # DATA[1] goes  here
                (data1_variant1), (data1_variant2), (data1_variant3), ('cmd', {types_info}, 'desc')
            ),
            (
                (data2_variant1), (data2_variant2), (data2_variant3)
            ),
        ],
    ],
]
