import random
import string
from copy import deepcopy

from components.Signals import SplitSignal
from components.SocialNetwork import SocialNetwork
from components.InteractionStrategies import InteractionStrategy, BeliefInteractionChoice
from components.Traits import ImmutableTraits, MutableTraits
from components.VotingStrategies import VotingStrategy, TrustVoteChoice


class Contestant:
    def __init__(
        self,
        name: str,
        voting_strategy: VotingStrategy = TrustVoteChoice(),
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
        self.immune_from_votes = False # TODO: Make it a mutable trait?

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

    def set_trust_preference(self, game_network, more_trusted, less_trusted):
        """Sets the trust values in the true network such that `more_trusted` is trusted more than `less_trusted`."""
        if (more_trusted or less_trusted) not in game_network.graph.nodes:
            raise ValueError("Both contestants must be in the network.")
        
        edge_more = game_network.graph[self][more_trusted]["relationship"]
        edge_less = game_network.graph[self][less_trusted]["relationship"]

        # Ensure more_trusted has higher trust
        val_more = max(edge_more.realized_trust[more_trusted.name], edge_less.realized_trust[less_trusted.name])
        val_less = min(edge_more.realized_trust[more_trusted.name], edge_less.realized_trust[less_trusted.name])
        edge_more.realized_trust[more_trusted.name] = val_more
        edge_less.realized_trust[less_trusted.name] = val_less  
        print(edge_more, edge_less)

    def update_trust_threshold(self, declared):
        """
        Update the believed trust threshold based on whether agents declare the agent kicked out was above or below it.
        """
        trusts = []
        for neighbour, data in self.estimated_social_network.graph[self].items():
            if neighbour in declared.graph.nodes:
                declared_trust = declared.graph[self][neighbour]["relationship"].realized_trust[self.name]
                if declared_trust is not None:
                    trusts.append(declared_trust)
        if trusts:
            self.immutable_traits.trust_threshold = sum(trusts) / len(trusts) 

    def get_vote(self):
        return self.voting_strategy.choose(self)

    def get_interaction(self, true_net, latest_vote = None):
        params = {"true_net":true_net, 
                  "voter": self, 
                  "latest_vote":latest_vote}
        return self.interaction_strategy.choose(**params)
        
    def _generate_random_name(self, length=6):
        # Fallback method in case no name is provided.
        return "".join(random.choices(string.ascii_uppercase, k=length))

    def _generate_estimated_social_network(self, first_impression: SocialNetwork):
        if self.estimated_social_network is not None:
            raise Exception(
                "Trying to generate an estimated social network where one already exists."
            )

        self.estimated_social_network = deepcopy(first_impression)
        
        # Link the real self and the estimated self
        myself = self.estimated_social_network.get_contestant_by_name(self.name)

        self.immune_from_votes = True
        for neighbour, data in self.estimated_social_network.graph[myself].items():
            # In the voter's mind, all neighbours observe the same network as them
            neighbour.estimated_social_network = self.estimated_social_network 
            neighbour.voting_strategy = TrustVoteChoice()

            # Check if the contestant believes they are safe from elimination
            if not data["relationship"].safe_link(neighbour): self.immune_from_votes = False
        
        print(f"{self.name} thinks they are {'safe' if self.immune_from_votes else 'not safe'} from elimination.")

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Contestant) and self.name == other.name

    def __repr__(self):
        return f"Contestant({self.name})"
