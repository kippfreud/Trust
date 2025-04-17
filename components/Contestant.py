import random
import string
from copy import deepcopy

from components.Signals import SplitSignal
from components.SocialNetwork import SocialNetwork
from components.InteractionStrategies import InteractionStrategy, BeliefInteractionChoice
from components.Traits import ImmutableTraits, MutableTraits
from components.VotingStrategies import VotingStrategy


class Contestant:
    def __init__(
        self,
        name: str,
        voting_strategy: VotingStrategy,
        interaction_strategy: InteractionStrategy = BeliefInteractionChoice(),
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
        self.immune_from_votes = False

    def generate_estimated_social_network(self, true_network):
        if self.estimated_social_network is not None:
            raise Exception(
                "Trying to generate an estimated social network where one already exists."
            )
        self.estimated_social_network = self._generate_estimated_social_network(
            true_network
        )
        for neighbour, data in self.estimated_social_network.graph[self].items():
            data["relationship"].trust_var[neighbour.name] = 100
        for c in self.estimated_social_network.iter_contestants():
            c.estimated_social_network = self.estimated_social_network

    def MC_simulate_games(self, n=100):
        """Will run `n` simulations of the game, based on the estimated social network of the contestant"""
        results = []
        for i in range(n):
            result = []
            self.estimated_social_network.sample_trust()
            for c in self.estimated_social_network.iter_contestants():
                c.immune_from_votes = False
            while True:
                c, _ = self.estimated_social_network.simulate_vote()
                result.append(c)
                if c == SplitSignal:
                    results.append(result)
                    break
                c.immune_from_votes = True
        self.estimated_social_network.clear_realized_trust()
        for c in self.estimated_social_network.iter_contestants():
            c.immune_from_votes = False
        result_dict = {}
        for i in range(1, 1 + len(self.estimated_social_network.get_all_contestants())):
            g_r = [r[i - 1] for r in results if len(r) >= i]
            result_dict[i] = {x: g_r.count(x) / len(g_r) for x in set(g_r)}
        return result_dict

    def get_true_trust(self):
        """Returns an array of neighbours-perceived_trust of a constestant."""
        trust_neighbours = {}
        for neighbour, data in self.estimated_social_network.graph[self].items():
            if data["relationship"].trust_var[self.name] == 0:
                trust_neighbours[neighbour] = data["relationship"].trust_mean[self.name]
            else:
                r_t = data["relationship"].realized_trust[self.name]
                assert (
                    r_t is not None
                ), "If trust variance > 0, realized trust must exist"
                trust_neighbours[neighbour] = r_t
        return trust_neighbours        

    def get_vote(self):
        return self.voting_strategy.choose(self)

    def get_interaction(self, true_net, latest_vote = None):
        params = {"true_net":true_net, 
                  "voter": self, 
                  "latest_vote":latest_vote}
        return self.interaction_strategy.choose(**params)
        
    def simulate_vote():
        # TODO: Choose how to simulate votes
        return None 

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
