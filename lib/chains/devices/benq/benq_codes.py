## rs232 codes
# Format:
# "<CR>*command=parameter#<CR>"
## Examples
# power on: <CR>*pow=on#<CR>
# power off: <CR>*pow=off#<CR>
# power status: <CR>*pow=?#<CR>

TOPICS = []


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
