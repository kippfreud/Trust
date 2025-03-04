import random
import string

from components.InteractionStrategies import InteractionStrategy
from components.Traits import ImmutableTraits, MutableTraits
from components.VotingStrategies import VotingStrategy


class Contestant:
    def __init__(
        self,
        name: str,
        voting_strategy: VotingStrategy,
        interaction_strategy: InteractionStrategy,
        immutable_traits: ImmutableTraits = ImmutableTraits(),
        mutable_traits: MutableTraits = MutableTraits(),
    ):
        # If a name is provided, use it; otherwise, fallback to a random name.
        self.name = name if name is not None else self._generate_random_name()
        self.voting_strategy = voting_strategy
        self.interaction_strategy = interaction_strategy
        self.immutable_traits = immutable_traits
        self.mutable_traits = mutable_traits
        self.estimated_social_network = None

    def get_trust(self):
        """Returns an array of neighbours-perceived_trust of a constestant."""
        trust_neighbours = {}
        for u, v, data in self.estimated_social_network.graph.edges(data=True):
            if self in {u,v}:
                # Convention for trust dictionary {u.name: trust(u->v), ... }
                neighbour = u if v is self else v
                trust_neighbours[neighbour] = data["relationship"].trust[self.name]
        return trust_neighbours

    def get_vote(self):
        return self.voting_strategy.choose(self)

    def get_interaction(self):
        return self.interaction_strategy.choose(self)

    def _generate_random_name(self, length=6):
        # Fallback method in case no name is provided.
        return "".join(random.choices(string.ascii_uppercase, k=length))

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Contestant) and self.name == other.name

    def __repr__(self):
        return f"Contestant({self.name})"
