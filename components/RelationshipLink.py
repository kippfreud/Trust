class RelationshipLink:
    def __init__(self, contestant1, contestant2):
        # Initialize directional trust values for each contestant (by name) and uncertainty.
        # TODO: What is the convention? Is the contestant name the source? 
        # eg. [('Filip', 0), ('Kipp', -1)] means trust(Filip -> Kipp) = 0 and trust(Kipp -> Filip) = -1.
        self.trust = {contestant1.name: 0, contestant2.name: 0}
        self.uncertainty = 0

    def __repr__(self):
        return f"RelationshipLink(trust={self.trust}, uncertainty={self.uncertainty})"
