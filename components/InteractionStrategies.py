import random
import numpy as np

class InteractionStrategy:
    def choose(self, voter):
        print("This function should be overwritten by derived class!")
        exit(1)


class RandomInteractionChoice(InteractionStrategy):
    def choose(self, voter):
        """
        In this strategy, the voter will choose 1 interaction and 1 target at random
        """
        possible_interacted = [
            c
            for c in voter.estimated_social_network.get_all_contestants()
            if c is not voter
        ]
        interacted = random.sample(possible_interacted, 1)
        possible_targets = [
            c
            for c in voter.estimated_social_network.get_all_contestants()
            if c not in interacted
        ]
        target = random.sample(possible_targets, 1)
        possible_interactions = [Increase_Trust, Decrease_Trust]
        interaction = random.choice(possible_interactions)
        return interaction(voter, interacted, target)

class Interaction:
    def __init__(self, interactor, interacted_group, target_group):
        """instantiate the intraction with the interactor, interacted_group, and target_group"""
        self.interactor = interactor
        self.interacted_group = interacted_group
        self.target_group = target_group

    def success(self, social_net):
        print("This function should be overwritten by derived class!")
        exit(1)

    def failure(self, social_net):
        print("This function should be overwritten by derived class!")
        exit(1)


class Increase_Trust(Interaction):
    def success(self, social_net):
        # On success, the interacted group will trust the target group more
        for a in self.interacted_group:
            for b in self.target_group:
                relationship = social_net.graph.get_edge_data(a, b)["relationship"]
                relationship.trust[a.name] += 1

    def failure(self, social_net):
        # On failure, the interacted group will trust the interactor less
        for a in self.interacted_group:
            relationship = social_net.graph.get_edge_data(a, self.interactor)[
                "relationship"
            ]
            relationship.trust[a.name] -= 1


class Decrease_Trust(Interaction):
    def success(self, social_net):
        # On success, the interacted group will trust the target group less
        for a in self.interacted_group:
            for b in self.target_group:
                relationship = social_net.graph.get_edge_data(a, b)["relationship"]
                relationship.trust[a.name] -= 1

    def failure(self, social_net):
        # On failure, the interacted group will trust the interactor less
        for a in self.interacted_group:
            relationship = social_net.graph.get_edge_data(a, self.interactor)[
                "relationship"
            ]
            relationship.trust[a.name] -= 1

class BeliefInteractionChoice(InteractionStrategy):
    def choose(self, voter):
        """
            In this strategy, the voter simulates the voting outcomes after t time steps and
            and chooses the interaction via backward induction 
        """
        # predicted_vote = voter.simulate_votes()
        myself = voter.name
        # Example
        predicted_vote = {1: {("kipp", 1): {"filip": 1/3, "luisa": 1/3, "split": 1/3}, 
                              ("luisa", 1): {"kipp": 3/5, "filip": 1/5, "split": 1/5}, 
                              ("filip", 1): {"kipp": 1/8, "luisa": 6/8, "split": 1/8}}}
        outcomes = []
        for t in predicted_vote.keys():
            for votes in predicted_vote[t]:
                contestants = [contestant[0] for contestant in votes.keys()] + ["split"]
                expected_votes = []
                for contestant in contestants:
                    votes_contestant = 0
                    for vote in votes.values():
                        votes_contestant += vote[contestant]
                    expected_votes.append(votes_contestant)
                outcome = contestants[np.argmin(np.array(expected_votes))]
                outcomes.append(outcome)
                print(f'{myself} thinks {outcome} will be the outcome after {t} rounds.')

        return RandomInteractionChoice().choose(voter)