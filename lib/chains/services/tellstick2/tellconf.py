import chains.service, copy, re, td, Queue, time
from chains.common import log
import types

def fromServiceConfig(config):

    base = config.get('tellstickconf')
    base['device'] = []

    if config.get('devices'):
        for key in config.get('devices'):
            device = {}
            source = config['devices'][key]
            if source.get('class') and source['class'] != 'command':
                continue
            if source.get('id'):
                device['id'] = source['id']
            else:
                log.error("Ignoring device because missing id: %s" % source)
                #raise Exception("Ignoring device because missing id: %s" % source)
                continue
            device['name'] = key
            #if source.get('name'): device['name'] = source['name']
            if source.get('controller'): device['controller'] = source['controller']
            if source.get('protocol'): device['protocol'] = source['protocol']
            if source.get('model'): device['model'] = source['model']
            if source.get('parameters'):
                device['parameters'] = {}
                for param in source['parameters']:
                    device['parameters'][param] = str(source['parameters'][param])
            base['device'].append(device)

    lines = []
    _render(base, lines, -1, '')
    text = '\n'.join(lines)

    return text

def write(text, path=None):
    if not path:
        path = '/etc/tellstick.conf'
    fp = open(path, 'w')
    fp.write(text.encode('utf-8'))
    fp.close()

def _render(config, lines, indent, parent):
    indent += 1
    if type(config) == types.DictType:
        for key in config:
            value = config[key]
            if type(value) == types.ListType:
                _render(value, lines, indent, key)
            elif type(value) == types.DictType:
                _formatLine(indent, lines, '%s {' % key)
                _render(value, lines, indent, '')
                _formatLine(indent, lines, '}')
            else:
                _formatLine(indent, lines, '%s = %s' % (key, _formatValue(config[key])))
    elif type(config) == types.ListType:
        for item in config:
            _formatLine(indent-1, lines, '%s {' % parent)
            _render(item, lines, indent-1, '')
            _formatLine(indent-1, lines, '}')

def _formatLine(indent, lines, string):
    lines.append( '%s%s' % ('  ' * indent, string) )

def _formatValue(value):
    if type(value) == types.IntType:
        return '%s' % value
    elif type(value) == types.FloatType:
        return '%s' % value
    elif type(value) == types.BooleanType:
        if value: return 'true'
        else:     return 'false'
    else:
        return '"%s"' % value
