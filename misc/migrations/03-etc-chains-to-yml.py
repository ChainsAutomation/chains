import os
import ConfigParser
import yaml

dirs = ['/etc/chains','/etc/chains/services']

def convert(oldPath, newPath):

    data = {}
    cp = ConfigParser.ConfigParser()
    cp.read(oldPath)

    for section in cp.sections():
        if not data.has_key(section):
            data[section] = {}
        for item in cp.items(section):
            key,val = item
            data[section][key] = val

    yml = yaml.dump(data, default_flow_style=False, width=1000)
    fp = open(newPath, 'w')
    fp.write(yml)
    fp.close() 

for dir in dirs:
    for f in os.listdir(dir):

        if f[0] == '.':
            continue
        ext = f.split('.').pop()
        if ext != 'conf':
            continue

        oldPath = dir + '/' + f
        newPath = dir + '/%s.yml' % f.split('.').pop(0)
        print "old: %s" % oldPath
        print "new: %s" % newPath

        if os.path.exists(newPath):
            print "- SKIP! Already exists"
        else:
            convert(oldPath, newPath)
            print "- CONVERTED"


print ""
print "All done, you should now:"
print "rm /etc/chains/*.conf /etc/chains/services/*.conf"
print ""
