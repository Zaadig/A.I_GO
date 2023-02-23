import Goban 
from random import choice
from copy import deepcopy
import math



def monte_carlo_tree_search(board, color, num_simulations):

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
                self.visits = 0
                self.wins = 0
                self.children = []

            def is_fully_expanded(self):
                return len(self.children) == len(self.board.legal_moves())

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
                    return self.wins / self.visits + 1.41 * math.sqrt(math.log(self.parent.visits) / self.visits)

            def simulate(self):
                winner = simulate_game(self.board)
                self.backpropagate(winner)

            def backpropagate(self, winner):
                self.visits += 1
                if winner == color:
                    self.wins += 1
                if self.parent:
                    self.parent.backpropagate(winner)

        # Create the root node of the search tree
        root_node = Node(board)

        # Run Monte Carlo Tree Search for the specified number of simulations
        for i in range(num_simulations):
            # Select a node to expand using the UCT algorithm
            node = root_node
            while not node.is_fully_expanded() and node.children:
                node = node.select_child()

            # Expand the selected node by adding a child node for a random legal move
            if not node.is_fully_expanded():
                node = node.expand(choice(node.board.legal_moves()))

            # Simulate a game from the new node and backpropagate the result
            node.simulate()

        # Select the best move based on the number of visits to each child node
        best_child = max(root_node.children, key=lambda child: child.visits)
        return best_child.move