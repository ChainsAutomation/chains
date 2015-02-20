from distutils.core import setup
import glob
import sys
import os

# thanks to python distutils cookbook.
def is_package(path):
    #print("Looking for: %s" % os.path.isfile(os.path.join(path, '__init__.py')))
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
        )

def find_packages(path, base="" ):
    """ Find all packages in path """
    packages = {}
    #print("os.listdir(path): %s" % str(os.listdir(path)))
    for item in os.listdir(path):
        fullpath = os.path.join(path, item)
        #print("path searched: %s" % fullpath)
        dir = os.path.join(path, item)
        if is_package( dir ):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            #packages[module_name] = dir
            packages["chains/devices/%s" % module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages

#find_packages(".")
#find_packages("lib/chains/devices/")
packs = find_packages("lib/chains/devices/")

devices = find_packages('lib/chains/devices/').keys()

setup(name='chains',
    version='0.9',
    description='Chains Home Automation',
    author='SS & CQ',
    author_email='devel@chainsautomation.com',
    url='http://chainsautomation.com',
    package_dir={'': 'lib'},
    # packages=['lib/ha', 'lib/ha/com', 'lib/ha/devices', 'lib/ha/daemon', 'lib/ha/listener', 'lib/ha/sequences', 'lib/ha/config'],
    packages=['chains', 'chains/commandline', 'chains/common', 'chains/device', 'chains/devices','chains/daemon', 'chains/manager', 'chains/orchestrator', 'chains/reactor']+devices,
    # py_modules=['foo'],
    )

