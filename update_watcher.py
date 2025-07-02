#!/usr/bin/env python3

import importlib
import sys
import time
import os
import traceback
import hashlib
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import ocp_vscode as ocp

ocp.set_port(3939)

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <object>")
    exit(0)

module_name = sys.argv[1]
module = None

watch_file = os.path.abspath(module_name + ".py")

watch_file_md5 = ""
ocp.set_colormap(ocp.ColorMap.golden_ratio())
ocp.set_defaults(reset_camera=ocp.Camera.KEEP)
lock = threading.Lock()

def update_handler():
    global module
    global watch_file_md5
    global lock

    if not lock.acquire(blocking=False):
        return

    try:
        md5 = hashlib.md5(open(watch_file, 'rb').read()).hexdigest()

        if md5 == watch_file_md5:
            return
        watch_file_md5 = md5

        print(f"Reloading {watch_file}..  ", end='')
        sys.stdout.flush()

        if not module:
            module = importlib.import_module(sys.argv[1])
        else:
            importlib.invalidate_caches()
            importlib.reload(module)

        ocp.show(*module.result.values(), names=list(module.result.keys()))

        print('  done (http://127.0.0.1:3939/viewer)')

    except Exception as e:
        print()
        print("#" * 80)
        print("  ERROR")
        print("#" * 80)
        print(traceback.format_exc())
        print("#" * 80)
        print()
    finally:
        lock.release()

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.abspath(event.src_path) == watch_file:
            update_handler()

update_handler()  # Run once at start

observer = Observer()
observer.schedule(ChangeHandler(), os.path.dirname(watch_file), recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
