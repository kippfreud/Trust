import random
import time

from components.Contestant import Contestant
from components.InteractionStrategies import RandomInteractionChoice
from components.SocialNetwork import SocialNetwork
from components.VotingStrategies import RandomVoteChoice


def main():
    # Instantiate the SocialNetwork, loading names from a JSON file.
    game_network = SocialNetwork(names_filename="names.json")

    contestants = []
    # Create 10 contestants, each assigned the next available name in order.
    for _ in range(30):
        contestant = Contestant(
            name=game_network.get_next_name(),
            voting_strategy=RandomVoteChoice(),
            interaction_strategy=RandomInteractionChoice(),
        )
        contestants.append(contestant)
        game_network.add_contestant(contestant)
    game_network.plot()

    for round_i in range(len(contestants)):
        game_network.plot()
        time.sleep(0.1)
        game_network.interaction_phase()
        game_network.voting_phase()
        if game_network.split:
            break
        game_network.reaction_phase()
        if len(game_network.get_all_contestants()) == 1:
            break

    game_network.plot()
    game_network.save_animation_as_gif()


if __name__ == "__main__":
    main()
