import random

class Traits:
    def __init__(self):
        pass

class ImmutableTraits(Traits):
    def __init__(self, naivety=0, trust_threshold=None):
        self.naivety = naivety
        self.trust_threshold = random.uniform(0, 1) if trust_threshold is None else trust_threshold
        print(f"Trust threshold set to {round(self.trust_threshold, 3)}")

class MutableTraits(Traits):
    def __init__(self, paranoia=0):
        self.paranoia = paranoia
