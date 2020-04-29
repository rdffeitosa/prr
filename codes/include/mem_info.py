###### Memory Info of a Linux machine.
from __future__ import print_function
from collections import OrderedDict

def meminfo():
 meminfo=OrderedDict()
 with open('/proc/meminfo') as f:
  for line in f:
   meminfo[line.split(':')[0]] = line.split(':')[1].strip()
 return meminfo