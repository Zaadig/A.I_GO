import math
import numpy as np
import Goban
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import time
from random import choice
from Predictor import position_predict

def get_stones_positions(board):
        black_stones = []
        white_stones = []
        flattened_board = board.get_board()
        for i in range(len(flattened_board)):
            if flattened_board[i] == 1:
                black_stones.append(Goban.Board.flat_to_name(i))
            elif flattened_board[i] == 2:
                white_stones.append(Goban.Board.flat_to_name(i))
        return black_stones, white_stones

def monte_carlo_tree_search(board, color, time_limit, max_batch_size=8):
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

    class Node:
        def __init__(self, board, parent=None, move=None):
            self.board = deepcopy(board)
            self.parent = parent
            self.move = move
            self.visits = 0
            self.wins = 0
            self.children = {}
            self.nn_evaluation = None

        def is_fully_expanded(self):
            return len(self.children) == len(self.board.legal_moves())

        def select_child(self):
            unexplored_moves = [move for move in self.board.legal_moves() if move not in self.children]
            if unexplored_moves:
                return self.expand(choice(unexplored_moves))
            else:
                return max(self.children.values(), key=lambda child: child.get_puct_score())

        def expand(self, move):
            new_board = deepcopy(self.board)
            new_board.push(move)
            new_node = Node(new_board, parent=self, move=move)
            self.children[move] = new_node
            return new_node

        def get_puct_score(self):
            if self.visits == 0:
                return float('inf')
            else:
                # Use a better exploration constant, e.g. 1/sqrt(2)
                exploration_constant = 1 / math.sqrt(2)
                return (self.wins / self.visits) + \
                    exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits) * self.nn_evaluation

        def backpropagate(self, winner):
            self.visits += 1
            if winner == color:
                self.wins += 1
            if self.parent:
                self.parent.backpropagate(winner)

    def evaluate_nodes(nodes):
        for node in nodes:
            black_stones, white_stones = get_stones_positions(node.board)
            node.nn_evaluation = position_predict(black_stones, white_stones)

    def worker(root_node):
        node = root_node
        while not node.is_fully_expanded() and node.children:
            node = node.select_child()

        if not node.is_fully_expanded():
            node = node.expand(choice(node.board.legal_moves()))

        if not node.nn_evaluation:
            evaluate_nodes([node])

        node.visits += 1
        winner = simulate_game(node.board)
        node.backpropagate(winner)
        node.visits -= 1

    root_node = Node(board)
    start_time = time.time()

    with ThreadPoolExecutor() as executor:
        while time.time() - start_time < time_limit:
            futures = [executor.submit(worker, root_node) for _ in range(max_batch_size)]
            for future in futures:
                future.result()

    # Use a more sophisticated endgame scoring method
    best_child = max(root_node.children.values(), key=lambda child: child.visits)
    return best_child.move
