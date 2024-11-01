import random
import string


class CustomMutator:
    def __init__(self, afl, max_size=1024):
        self.afl = afl
        self.max_size = max_size

    def generate_integer(self, length):
        return
