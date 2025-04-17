import random
import numpy as np
from components.Signals import SplitSignal

class InteractionStrategy:
    """
    An Interaction Strategy should implement a choose() function that can handle the key_params:
    true_net
    voter
    latest_vote
    """
    def choose(self, **kwargs): #true_net, voter):
        raise Exception("This function should be overwritten by derived class!")


class RandomInteractionChoice(InteractionStrategy):
    def choose(self, true_net, voter, latest_vote):
        """
        In this strategy, the voter will choose 1 interaction and 1 target at random
        """
        possible_interacted = [
            c for c in true_net.get_all_contestants() if c is not voter
        ]
        interacted = random.sample(possible_interacted, 1)
        possible_targets = [
            c for c in true_net.get_all_contestants() if c not in interacted
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
        raise Exception("This function should be overwritten by derived class!")

    def failure(self, social_net):
        raise Exception("This function should be overwritten by derived class!")


class Increase_Trust(Interaction):
    def success(self, social_net):
        # On success, the interacted group will trust the target group more
        for a in self.interacted_group:
            for b in self.target_group:
                relationship = social_net.graph.get_edge_data(a, b)["relationship"]
                relationship.trust_mean[a.name] += 1

                a.estimated_social_network.graph.get_edge_data(a, b)[
                    "relationship"
                ].trust_mean[a.name] += 1
                b.estimated_social_network.graph.get_edge_data(a, b)[
                    "relationship"
                ].trust_mean[a.name] += 1

    def failure(self, social_net):
        # On failure, the interacted group will trust the interactor less
        for a in self.interacted_group:
            relationship = social_net.graph.get_edge_data(a, self.interactor)[
                "relationship"
            ]
            relationship.trust_mean[a.name] -= 1
            a.estimated_social_network.graph.get_edge_data(a, self.interactor)[
                "relationship"
            ].trust_mean[a.name] -= 1
            self.interactor.estimated_social_network.graph.get_edge_data(
                a, self.interactor
            )["relationship"].trust_mean[a.name] -= 1


class Decrease_Trust(Interaction):
    def success(self, social_net):
        # On success, the interacted group will trust the target group less
        for a in self.interacted_group:
            for b in self.target_group:
                relationship = social_net.graph.get_edge_data(a, b)["relationship"]
                relationship.trust_mean[a.name] -= 1
                a.estimated_social_network.graph.get_edge_data(a, b)[
                    "relationship"
                ].trust_mean[a.name] -= 1
                b.estimated_social_network.graph.get_edge_data(a, b)[
                    "relationship"
                ].trust_mean[a.name] -= 1

    def failure(self, social_net):
        # On failure, the interacted group will trust the interactor less
        for a in self.interacted_group:
            relationship = social_net.graph.get_edge_data(a, self.interactor)[
                "relationship"
            ]
            relationship.trust_mean[a.name] -= 1
            a.estimated_social_network.graph.get_edge_data(a, self.interactor)[
                "relationship"
            ].trust_mean[a.name] -= 1
            self.interactor.estimated_social_network.graph.get_edge_data(
                a, self.interactor
            )["relationship"].trust_mean[a.name] -= 1

class BeliefInteractionChoice(InteractionStrategy):
    def choose(self, true_net, voter, latest_vote):
        """
            In this strategy, the voter simulates the voting outcomes after t time steps and
            and chooses the interaction via backward induction 
        """
        # predicted_vote = voter.simulate_votes()
        myself = voter.name
        num_contestants = len(true_net.get_all_contestants())

        # Simulate votes
        predicted_vote = voter.MC_simulate_games()

        for t in predicted_vote.keys():
            p_ko = predicted_vote[t][myself] # Probability of being kicked out
            p_s = predicted_vote[t][SplitSignal] # Probability of split prize
            p_mo = 1 - (p_ko + p_s) # Probability of moving on

        # Defense strategy when I believe I'll be kicked out in the next round
        if predicted_vote[1][myself] == max(predicted_vote[1].values()):
            predicted_vote[1].pop(myself)
            if predicted_vote[1][SplitSignal] == max(predicted_vote[1].values()):
                # Try to increase trust so prize is split
                # TODO: Clean how to choose the target_group
                print(f"{myself} will increase trust with everyone.")
                return Increase_Trust(voter, true_net.get_all_contestants(), voter)
            else:
                predicted_vote[1].pop(SplitSignal)
                sabotage = 
                sorted_vote = dict(sorted(predicted_vote[t].items(), key=lambda item: item[1], reverse=True)) 

        else: return  RandomInteractionChoice().choose(true_net, voter) 
            for votes in :
                
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

        return 