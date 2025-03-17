import random
import time
from copy import deepcopy

from components.Contestant import Contestant
from components.InteractionStrategies import RandomInteractionChoice
from components.SocialNetwork import SocialNetwork
from components.VotingStrategies import RandomVoteChoice, TrustVoteChoice


def main():
    # Instantiate the SocialNetwork, loading names from a JSON file.
    game_network = SocialNetwork(names_filename="names.json")

    contestants = []
    # Create 10 contestants, each assigned the next available name in order.
    for _ in range(5):
        contestant = Contestant(
            name=game_network.get_next_name(),
            # voting_strategy=RandomVoteChoice(),
            voting_strategy=TrustVoteChoice(),
            interaction_strategy=RandomInteractionChoice(),
        )
        contestants.append(contestant)
        game_network.add_contestant(contestant)
    # game_network.plot()

    # Estimated social networks are generated here
    copynet = deepcopy(game_network)
    for c in game_network.iter_contestants():
        c.generate_estimated_social_network(copynet)
    del copynet

    for round_i in range(len(contestants)):
        game_network.plot()
        time.sleep(0.1)
        game_network.interaction_phase()
        for c in game_network.iter_contestants():
            ret = c.estimated_social_network.simulate_vote()
            print(f"{c} Thinks {ret[0]} will be evicted!")
        outcome = game_network.voting_phase()
        if game_network.split:
            break
        game_network.voting_outcome_reaction_phase(outcome)
        if len(game_network.get_all_contestants()) == 1:
            break

    game_network.plot()
    game_network.save_animation_as_gif()


if __name__ == "__main__":
    main()
