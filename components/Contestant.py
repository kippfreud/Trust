import random
import string
from copy import deepcopy

from components.InteractionStrategies import InteractionStrategy
from components.Traits import ImmutableTraits, MutableTraits
from components.VotingStrategies import VotingStrategy
from components.SocialNetwork import SocialNetwork

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

    def generate_estimated_social_network(self, true_network):
        if self.estimated_social_network is not None:
            raise Exception("Trying to generate an estimated social network where one already exists.")
        self.estimated_social_network = self._generate_estimated_social_network(true_network)
        for c in self.estimated_social_network.iter_contestants():
            c.estimated_social_network = self.estimated_social_network

    def get_perceived_trust(self):
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

    def get_interaction(self, true_net):
        return self.interaction_strategy.choose(true_net, self)

    def _generate_random_name(self, length=6):
        # Fallback method in case no name is provided.
        return "".join(random.choices(string.ascii_uppercase, k=length))

    def _generate_estimated_social_network(self, true_network: SocialNetwork):
        return deepcopy(true_network)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Contestant) and self.name == other.name

    def __repr__(self):
        return f"Contestant({self.name})"
