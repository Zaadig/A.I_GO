import math
import Goban
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import time
from random import choice
from Predictor import position_predict

#------------------------------------------------------------------------------------------------------------------------------------------------------------

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



def monte_carlo_tree_search(board, color, time_limit, max_batch_size=8, temperature=1):

    # Simulates a game until the end and returns the winner
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

    # Define the Node class, which represents a node in the MCTS tree
    class Node:
        def __init__(self, board, parent=None, move=None):
            self.board = deepcopy(board)
            self.parent = parent
            self.move = move
            self.visits = 0
            self.wins = 0
            self.children = {}
            self.nn_evaluation = 0.5

        # Check if all possible moves from this node have been explored
        def is_fully_expanded(self):
            return len(self.children) == len(self.board.legal_moves())

        # Select the child node with the highest PUCT score
        def select_child(self):
            unexplored_moves = [move for move in self.board.legal_moves() if move not in self.children]
            if unexplored_moves:
                return self.expand(choice(unexplored_moves))
            else:
                return max(self.children.values(), key=lambda child: child.get_puct_score())

        # Expand the current node by adding a new child node for the given move
        def expand(self, move):
            if self.board.is_game_over():
                return self  # return the current node without expanding
            new_board = deepcopy(self.board)
            new_board.push(move)
            new_node = Node(new_board, parent=self, move=move)
            self.children[move] = new_node
            return new_node
        # Calculate the PUCT score for the current node
        def get_puct_score(self):
            if self.visits == 0:
                return float('inf')
            else:
                # Use temperature to control exploration
                exploration_constant = 1 / math.sqrt(2)
                exploitation_score = self.wins / self.visits
                exploration_score = exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)
                position_score = self.nn_evaluation if color == Goban.Board._BLACK else (1 - self.nn_evaluation)

                # Consider position evaluation in addition to the number of wins and visits
                return (exploitation_score + exploration_score) * (1 + temperature * position_score)

        # Backpropagate the result of the simulation to the parent nodes
        def backpropagate(self, winner):
            self.visits += 1
            if winner == color:
                self.wins += 1
            if self.parent:
                self.parent.backpropagate(winner)

    # Evaluate the position of the nodes in the given list using a neural network
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
    
    # Gradually decrease temperature over time
    temperature = max(0.01, temperature * 0.99)

    # Use a more sophisticated endgame scoring method
    best_child = max(root_node.children.values(), key=lambda child: child.visits)
    return best_child.move