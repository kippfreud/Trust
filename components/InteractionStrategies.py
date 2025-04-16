import random


class InteractionStrategy:
    def choose(self, true_net, voter):
        raise Exception("This function should be overwritten by derived class!")


class RandomInteractionChoice(InteractionStrategy):
    def choose(self, true_net, voter):
        """
        In this strategy, the voter will choose 1 interacter and 1 target at random
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
