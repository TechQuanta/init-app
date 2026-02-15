import time
import itertools
import threading
from colorama import Fore, Style


class Spinner:
    def __init__(self, message="Loading"):
        self.message = message
        self.spinner = itertools.cycle(
            ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        )
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.animate)
        self.thread.start()

    def animate(self):
        while self.running:
            print(
                Fore.WHITE + Style.DIM + f"\r{next(self.spinner)} {self.message}...",
                end="",
            )
            time.sleep(0.05)

    def stop(self):
        self.running = False
        self.thread.join()
        print("\r", end="")  # Clean spinner line
