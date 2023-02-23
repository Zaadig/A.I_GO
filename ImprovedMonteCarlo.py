import numpy as np
import math
from multiprocessing import Pool, cpu_count
from copy import deepcopy
import Goban
from random import choice

# Define a function to simulate a game and return the winner
def simulate_game(board):
    board_cpy = deepcopy(board)
    while not board_cpy.is_game_over():
        move = choice(board_cpy.legal_moves())
        board_cpy.push(move)
    result = board_cpy.result()
    if result == "1-0":
        return Goban.Board._WHITE
    elif result == "0-1":
        return Goban.Board._BLACK
    else:
        return Goban.Board._EMPTY

# Define a class to represent the nodes in the search tree
class Node:
    def __init__(self, board, parent=None, move=None):
        self.board = deepcopy(board)
        self.parent = parent
        self.move = move
        self.visits = np.zeros(1)
        self.wins = np.zeros(1)
        self.children = []
        self.legal_moves = list(self.board.legal_moves())

    def is_fully_expanded(self):
        return len(self.children) == len(self.legal_moves)

    def select_child(self):
        unexplored_moves = [move for move in self.legal_moves
                            if move not in [child.move for child in self.children]]
        if unexplored_moves:
            return self.expand(np.random.choice(unexplored_moves))
        else:
            return max(self.children, key=lambda child: child.get_uct_score())

    def expand(self, move):
        new_board = deepcopy(self.board)
        new_board.push(move)
        new_node = Node(new_board, parent=self, move=move)
        self.children.append(new_node)
        return new_node

    def get_uct_score(self):
        if self.visits == 0:
            return float('inf')
        else:
            return (self.wins / self.visits) + 1.41 * math.sqrt(math.log(self.parent.visits) / self.visits)

    def simulate(self, color):
        winner = simulate_game(self.board)
        self.backpropagate(winner, color)

    def backpropagate(self, winner, color):
        self.visits += 1
        if winner == color:
            self.wins += 1
        if self.parent:
            self.parent.backpropagate(winner, color)

# Define simulate_and_backpropagate as a top-level function
def simulate_and_backpropagate(node, color):
    node.simulate(color)

def monte_carlo_tree_search(board, color, num_simulations):
    # Create the root node
    root = Node(board)

    # Run Monte Carlo Tree Search for the specified number of simulations
    with Pool(cpu_count()) as p:
        for i in range(num_simulations):
            # Select a node to expand using the UCT algorithm
            node = root
            while not node.is_fully_expanded() and node.children:
                node = node.select_child()

            # Expand the selected node by adding a child node for a random legal move
            if not node.is_fully_expanded():
                    node = node.expand(choice(node.board.legal_moves()))
                    winner = simulate_game(node.board)
                    node.backpropagate(winner, color)
            else:
            # Create an iterable of tuples, where each tuple contains a child node and the color argument
                args = ((child, color) for child in node.children)
                p.starmap(simulate_and_backpropagate, args)
     # Return the best move found by MCTS
    return max(root.children, key=lambda child: child.visits).move