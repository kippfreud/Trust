import random

from components.Signals import SplitSignal


class VotingStrategy:
    def choose(self, voter):
        print("This function should be overwritten by derived class!")
        exit(1)


class RandomVoteChoice(VotingStrategy):
    def choose(self, voter):
        contestants = [
            c
            for c in voter.estimated_social_network.get_all_contestants()
            if c is not voter
        ]
        return random.choice(contestants + [SplitSignal])
