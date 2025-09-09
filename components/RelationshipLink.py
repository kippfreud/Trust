class RelationshipLink:
    def __init__(self, contestant1, contestant2):
        # Initialize directional trust values for each contestant (by name) and uncertainty.
        # Convention: realized_trust name is the target.
        # eg. {'Filip': 0.3, 'Kipp': 0.5} means trust(Kipp -> Filip) = 0.3 and trust(Filip -> Kipp) = 0.5.
        self.realized_trust = {contestant1.name: None, contestant2.name: None}
        self.trust_mean = {contestant1.name: 0, contestant2.name: 0}
        self.trust_var = {contestant1.name: 0, contestant2.name: 0}

    def __repr__(self):
        #return f"RelationshipLink(trust={self.trust_mean}, var={self.trust_var}, realized={self.realized_trust})"
        return f"RelationshipLink(realized={self.realized_trust})"
    
    def safe_link(self, contestant):
        """Asks if the contestant believes they are above the other's trust threshold."""
        if contestant.name not in self.realized_trust.keys():
            raise ValueError("Contestant not part of this relationship link.")
        
        my_name = list(self.realized_trust.keys() - {contestant.name})
        if len(my_name) != 1:
            raise ValueError("There should be exactly one other contestant in this relationship link.")
        
        return  contestant.immutable_traits.trust_threshold < self.realized_trust[my_name[0]]
