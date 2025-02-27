class Traits:
    def __init__(self):
        pass


class ImmutableTraits(Traits):
    def __init__(self, naivety=0):
        self.naivety = naivety


class MutableTraits(Traits):
    def __init__(self, paranoia=0):
        self.paranoia = paranoia
