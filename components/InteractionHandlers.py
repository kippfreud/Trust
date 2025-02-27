import random


class InteractionHandler:
    def get_interaction_success(self, net, interaction):
        print("This function should be overwritten by derived class!")
        exit(1)


class RandomInteractionHandler(InteractionHandler):
    """
    With this handler, interactions are randomly successful or failing.
    """

    def __init__(self, success_prob: float = 0.75):
        self.success_prob = success_prob

    def get_interaction_success(self, net, interaction):
        return random.uniform(0, 1) < self.success_prob
