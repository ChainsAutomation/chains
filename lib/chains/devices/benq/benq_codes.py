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
            ['amxdd', 'AMX Device Discovery'],
            ['macaddr', 'MAC Address'],
            ['Highaltitude', 'High Altitude Mode'],
]


MODELS = [
        'W6000',
        'W6500',
]

CMDS = [
        'power_on',
        'power_off',
]

CODES = {
         0x01: 'power_on',
         0x02: 'power_off',
}
