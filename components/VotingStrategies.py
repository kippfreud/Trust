import random

import numpy as np

from components.Signals import SplitSignal


class VotingStrategy:
    def choose(self, voter):
        raise Exception("This function should be overwritten by derived class!")


class RandomVoteChoice(VotingStrategy):
    def choose(self, voter):
        contestants = [
            c
            for c in voter.estimated_social_network.get_all_contestants()
            if c is not voter and not c.immune_from_votes
        ]
        return random.choice(contestants + [SplitSignal])


class TrustVoteChoice(VotingStrategy):
    """
    Trust-based vote: Split if voter trusts all its neighbours at least voter.trust_threshold
    """

    def choose(self, voter):
        trust = {
            c: t for c, t in voter.get_true_trust().items() if not c.immune_from_votes
        }
        trust_voter = np.array(list(trust.items()))
        if trust == {}:
            # There is nobody to choose, we must split
            return SplitSignal
        elif (
            all(trust_voter[:, 1] > voter.immutable_traits.trust_threshold)
            or len(trust_voter) == 0
        ):
            return SplitSignal
        else:
            # Choose any agent with lowest trust score
            vote_out = np.random.choice(
                np.where(trust_voter[:, 1] == np.min(trust_voter[:, 1]))[0]
            )
            return trust_voter[vote_out, 0]
