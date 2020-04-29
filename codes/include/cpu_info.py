###### CPU Info of a Linux machine.
### Picked from: http://echorand.me/site/notes/articles/python_linux/article.html
from __future__ import print_function
from collections import OrderedDict
import pprint
 
def cpuinfo():
 cpuinfo=OrderedDict()
 procinfo=OrderedDict()
 nprocs = 0
 with open('/proc/cpuinfo') as f:
  for line in f:
   if not line.strip():
    cpuinfo['proc%s' % nprocs] = procinfo
    nprocs=nprocs+1
    procinfo=OrderedDict()
   else:
    if len(line.split(':')) == 2:
     procinfo[line.split(':')[0].strip()] = line.split(':')[1].strip()
    else:
     procinfo[line.split(':')[0].strip()] = ''
 return cpuinfo