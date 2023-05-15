import threading
import itertools
import time
import sys

class Spinner:
    def __init__(self, message='Loading...', delay=0.1):
        self.spinner = itertools.cycle(['-', '/', '|', '\\'])
        self.delay = delay
        self.spinner_active = False
        self.spinner_thread = threading.Thread(target=self.init_spinner)
        self.message = message

    def start(self):
        self.spinner_active = True
        self.spinner_thread.start()

    def stop(self):
        self.spinner_active = False
        self.spinner_thread.join()

    def init_spinner(self):
        while self.spinner_active:
            sys.stdout.write(next(self.spinner))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()
