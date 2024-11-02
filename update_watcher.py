#!/usr/bin/env python3

import importlib
import sys
import time
import fcntl
import os
import signal
import traceback
import hashlib

import yacv_server as yacv

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <object>")
    exit(0)

module_name = sys.argv[1]
print(f"Import module {module_name}")
module = importlib.import_module(sys.argv[1])
    
watch_file = os.path.abspath(module_name + ".py")
watch_dir = os.path.dirname(watch_file)

watch_file_md5 = ""

def update_handler(signum, frame):
    global module
    global watch_file_md5

    md5 = hashlib.md5(open(watch_file, 'rb').read()).hexdigest()

    if md5 == watch_file_md5:
        return
    watch_file_md5 = md5

    print(f"Reloading {watch_file}..", end='')
    sys.stdout.flush()
    
    try:
        importlib.reload(module)
        yacv.clear()
        for k,v in module.result.items():
            yacv.show(v, names=k, auto_clear=False)
    except Exception as e:
        print()
        print("#" * 80)
        print("  ERROR")
        print("#" * 80)
        print(traceback.format_exc())
        print("#" * 80)
        print()

    print(' done (http://127.0.0.1:32323/)')
        
update_handler(0,0)
        
signal.signal(signal.SIGIO, update_handler)
fd = os.open(watch_dir,  os.O_RDONLY)
fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
fcntl.fcntl(fd, fcntl.F_NOTIFY,
            fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)

while True:
    time.sleep(10000)
