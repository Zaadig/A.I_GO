import numpy as np
import Goban 
from random import choice
from copy import deepcopy
import math
from myNeuralNetwork import position_predict
from numpy.random import default_rng

def get_stones_positions(board):
    black_stones = []
    white_stones = []
    flattened_board = np.array(board.get_board())
    black_stones = np.argwhere(flattened_board == Goban.Board._BLACK)
    white_stones = np.argwhere(flattened_board == Goban.Board._WHITE)
    black_stones = [Goban.Board.flat_to_name(pos) for pos in black_stones]
    white_stones = [Goban.Board.flat_to_name(pos) for pos in white_stones]
    return black_stones, white_stones


def monte_carlo_tree_search(board, color, num_simulations):
    
    def simulate_game(board):
        board_cpy = board.copy()
        rng = default_rng()
        while not board_cpy.is_game_over():
            move = rng.choice(board_cpy.legal_moves())
            board_cpy.push(move)
        result = board_cpy.result()
        if result == "1-0":
            return Goban.Board._WHITE
        elif result == "0-1":
            return Goban.Board._BLACK
        else:
            return Goban.Board._EMPTY

    class Node:
        def __init__(self, board, parent=None, move=None):
            self.board = board
            self.parent = parent
            self.move = move
            self.visits = 0
            self.wins = 0
            self.children = []
            black_stones, white_stones = get_stones_positions(self.board)
            self.nn_evaluation = position_predict(black_stones, white_stones)

        def is_fully_expanded(self):
            explored_moves = {child.move for child in self.children}
            return len(explored_moves) == len(self.board.legal_moves())

        def select_child(self):
            unexplored_moves = [move for move in self.board.legal_moves()
                                if move not in [child.move for child in self.children]]
            if unexplored_moves:
                return self.expand(choice(unexplored_moves))
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
                uct_score = (self.wins / self.visits) + \
                    1.41 * math.sqrt(math.log(self.parent.visits) / self.visits) + \
                    self.nn_evaluation
            return uct_score if self.parent is None else uct_score - self.parent.nn_evaluation

        def simulate(self):
            winner = simulate_game(self.board)
            self.backpropagate(winner)

        def backpropagate(self, winner):
            self.visits += 1
            if winner == color:
                self.wins += 1
            if self.parent:
                self.parent.backpropagate(winner)

    root_node = Node(board)

    for i in range(num_simulations):
        node = root_node
        while not node.is_fully_expanded() and node.children:
            node = node.select_child()

        if not node.is_fully_expanded():
            node = node.expand(choice(node.board.legal_moves()))

        node.simulate()

    best_child = max(root_node.children, key=lambda child: child.visits)
    return best_child.move