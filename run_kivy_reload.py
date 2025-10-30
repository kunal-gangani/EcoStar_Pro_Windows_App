import sys, os, time, subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

KIVY_APP = "RegisterPage.py"  # your Kivy file

class ReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print("\n🔁 Code changed — restarting app...\n")
            os.execv(sys.executable, [sys.executable, KIVY_APP])

if __name__ == "__main__":
    event_handler = ReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()

    try:
        subprocess.run([sys.executable, KIVY_APP])
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
