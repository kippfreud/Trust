import matplotlib
import networkx as nx

matplotlib.use("TkAgg")
import json
from collections import Counter

import imageio
import matplotlib.pyplot as plt
import numpy as np

from components.InteractionHandlers import (InteractionHandler,
                                            RandomInteractionHandler)
from components.RelationshipLink import RelationshipLink
from components.Signals import SplitSignal


class SocialNetwork:
    def __init__(
        self,
        n_interactions: int = 1,
        interaction_handler: InteractionHandler = RandomInteractionHandler(),
        names_filename=None,
    ):
        # Game params
        self.n_interactions = n_interactions

        # Game state
        self.split = False
        self.graph = nx.Graph()
        self.current_round = 0

        # Game tools
        self.interaction_handler = interaction_handler

        # Other Data
        self.available_names = []
        if names_filename:
            with open(names_filename, "r") as f:
                self.available_names = json.load(f)

        # Plotting Utils
        self.pos = {}
        self.fig = None
        self.ax = None
        self.ax_lim = None
        self.frames = []

    def voting_phase(self):
        """
        Will collect votes for all contestants, and either evict a contestant or end the game if all split
        :return: The removed contestant
        """
        sim_vote = self.simulate_vote()
        if sim_vote[0] is None:
            self.split = True
            print("Splitting Money")
            return None
        else:
            print(f"Evicting {sim_vote[0]}: Count = {sim_vote[1]}")
            self.remove_contestant(sim_vote[0])
            return sim_vote[0]

    def simulate_vote(self):
        """
        Generates the results of a vote. No actions will be taken.
        """
        votes = []
        for c in self.iter_contestants():
            votes.append(c.get_vote())
        count = Counter(votes)
        if len(count.keys()) == 1 and list(count.keys())[0] == SplitSignal:
            self.split = True
            return None, None
        else:
            if SplitSignal in count.keys():
                count.pop(SplitSignal)
            evicted = count.most_common(1)[0][0]
            return evicted, count

    def interaction_phase(self):
        """
        each agent can attempt self.n_interactions interactions
        """
        interactions = []
        for c in self.iter_contestants():
            interactions.append(c.get_interaction(self))
        for interaction in interactions:
            if self.interaction_handler.get_interaction_success(self, interaction):
                interaction.success(self)
            else:
                interaction.failure(self)

    def voting_outcome_reaction_phase(self, outcome):
        """
        Agents react to the previous vote, and adjust their internal parameters.
        Currently, only outcome which will be reacted to is the voting out of a
        contestant, in which case all contestants update their internal social
        net to reflect the eviction.
        """
        for c in self.iter_contestants():
            c.estimated_social_network.remove_contestant(outcome)

    def iter_contestants(self):
        """Returns an iterator over all contestants in the network."""
        return iter(self.graph.nodes)

    def get_all_contestants(self):
        """Returns a list of all contestants in the network."""
        return list(self.graph.nodes)

    def get_next_name(self):
        if self.available_names:
            return self.available_names.pop(0)
        else:
            return None

    def add_contestant(self, contestant):
        if contestant.name is None:
            next_name = self.get_next_name()
            if next_name:
                contestant.name = next_name
        self.graph.add_node(contestant)
        for other in self.graph.nodes:
            if other != contestant and not self.graph.has_edge(contestant, other):
                rel_link = RelationshipLink(contestant, other)
                self.graph.add_edge(contestant, other, relationship=rel_link)

    def remove_contestant(self, contestant):
        if self.graph.has_node(contestant):
            self.graph.remove_node(contestant)
        else:
            raise ValueError(f"WARNING: There is no contestant {contestant}")

    def capture_frame(self):
        """Capture the current figure canvas as an RGB image and store it."""
        # Ensure the canvas is drawn.
        self.fig.canvas.draw()
        # For TkAgg, use print_to_buffer() to get the image data.
        buf, (w, h) = self.fig.canvas.print_to_buffer()
        img = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 4))
        # Remove the alpha channel.
        img = img[..., :3]
        self.frames.append(img)

    def plot(self, fixed=True, record=True):
        """
        Updates the persistent plot non-blockingly in a single window.
        The axes limits never shrink: once set, they only expand if new node positions require it.
        Displays a title "A Game of Trust - Round i" (where i increments each time this function is called)
        and captures the frame if record=True.
        """
        # Create persistent figure and axes if they don't exist or have been closed.
        if self.fig is None or not plt.fignum_exists(self.fig.number):
            self.fig, self.ax = plt.subplots(figsize=(10, 8))
            plt.ion()  # enable interactive mode
            self.fig.show()  # show the figure once

        # Clear previous contents.
        self.ax.clear()

        # Increment the round counter and set the figure-level title.
        self.current_round += 1
        self.fig.suptitle(f"A Game of Trust - Round {self.current_round}", fontsize=16)

        # Compute or update layout.
        if not self.pos or not fixed:
            self.pos = nx.spring_layout(self.graph, seed=42)
        else:
            self.pos = {
                node: pos for node, pos in self.pos.items() if node in self.graph.nodes
            }

        # Draw nodes, edges, and labels.
        nx.draw_networkx_nodes(
            self.graph, self.pos, ax=self.ax, node_size=500, node_color="lightblue"
        )
        nx.draw_networkx_edges(self.graph, self.pos, ax=self.ax)
        labels = {node: node.name for node in self.graph.nodes}
        nx.draw_networkx_labels(self.graph, self.pos, labels, ax=self.ax, font_size=10)

        # Annotate edges with trust values.
        edge_labels = {}
        for u, v, data in self.graph.edges(data=True):
            rel_link = data["relationship"]
            trust_str = ", ".join(
                [f"{name}:{val}" for name, val in rel_link.trust.items()]
            )
            edge_labels[(u, v)] = trust_str
        nx.draw_networkx_edge_labels(
            self.graph, self.pos, edge_labels=edge_labels, ax=self.ax, font_color="red"
        )

        # Compute current limits from node positions.
        xs = [pos[0] for pos in self.pos.values()]
        ys = [pos[1] for pos in self.pos.values()]
        if xs and ys:
            margin_x = (max(xs) - min(xs)) * 0.1 if (max(xs) - min(xs)) != 0 else 0.1
            margin_y = (max(ys) - min(ys)) * 0.1 if (max(ys) - min(ys)) != 0 else 0.1
            current_xlim = (min(xs) - margin_x, max(xs) + margin_x)
            current_ylim = (min(ys) - margin_y, max(ys) + margin_y)
        else:
            current_xlim = (-1, 1)
            current_ylim = (-1, 1)

        # Set or update persistent axis limits: expand if needed, but never shrink.
        if self.ax_lim is None:
            self.ax_lim = (
                current_xlim[0],
                current_xlim[1],
                current_ylim[0],
                current_ylim[1],
            )
        else:
            new_xmin = min(self.ax_lim[0], current_xlim[0])
            new_xmax = max(self.ax_lim[1], current_xlim[1])
            new_ymin = min(self.ax_lim[2], current_ylim[0])
            new_ymax = max(self.ax_lim[3], current_ylim[1])
            self.ax_lim = (new_xmin, new_xmax, new_ymin, new_ymax)

        self.ax.set_xlim(self.ax_lim[0], self.ax_lim[1])
        self.ax.set_ylim(self.ax_lim[2], self.ax_lim[3])
        self.ax.axis("off")

        # Update the figure non-blockingly.
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.001)

        # Capture the frame if recording is enabled.
        if record:
            self.capture_frame()

    def save_animation_as_gif(self, filename="animation.gif", duration=200):
        """
        Save the recorded frames as an animated GIF.
        Make sure that recording has been enabled during plotting (record=True).
        """
        if self.frames:
            imageio.mimsave(filename, self.frames, duration=duration)
            print(f"Animation saved as {filename}")
        else:
            print("No frames were recorded; animation not saved.")
