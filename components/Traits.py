class Traits:
    def __init__(self):
        pass


class ImmutableTraits(Traits):
    def __init__(self, naivety=0, trust_threshold=-1):
        self.naivety = naivety
        self.trust_threshold = trust_threshold

class MutableTraits(Traits):
    def __init__(self, paranoia=0):
        self.paranoia = paranoia
