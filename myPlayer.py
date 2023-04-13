# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban
from random import choice
from copy import deepcopy
from playerInterface import *

class myPlayer(PlayerInterface):
    ''' Example of a random player for the go. The only tricky part is to be able to handle
    the internal representation of moves given by legal_moves() and used by push() and 
    to translate them to the GO-move strings "A1", ..., "J8", "PASS". Easy!

    '''

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None

    def getPlayerName(self):
        return "alpha-beta player"
    
    def opening1(self):
        # Play a stone on the third line of the star point, at D4 or E4
        if self._board[33] == Goban.Board._EMPTY and self._board[34] == Goban.Board._EMPTY:
            if self._mycolor == Goban.Board._BLACK:
                return "D4"
            else:
                return "E4"
        return None

    def opening2(self):
        # Play a stone on the fourth line of the star point, at D5 or E5
        if self._board[43] == Goban.Board._EMPTY and self._board[44] == Goban.Board._EMPTY:
            if self._mycolor == Goban.Board._BLACK:
                return "D5"
            else:
                return "E5"
        return None

    def opening3(self):
        # Play a stone on the third line of the star point, at C3 or F3
        if self._board[23] == Goban.Board._EMPTY and self._board[26] == Goban.Board._EMPTY:
            if self._mycolor== Goban.Board._BLACK:
                return "C3"
            else:
                return "F3"
        return None
    
    def play_big_move(self):
        # Get the legal moves for the current player
        legal_moves = [self._board.flat_to_name(m) for m in self._board.legal_moves()]

        # Check if any of the legal moves correspond to a big move
        big_moves = ['D4', 'D16', 'J4', 'J16']
        for move in big_moves:
            if move in legal_moves:
                print("Playing a big move: ", move)
                self._board.push(self._board.name_to_flat(move))
                return move

        # If no big moves are available, return None
        return None


    def getPlayerMove(self):


        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"
        

        # Get the legal moves for the current player
        legal_moves = [self._board.flat_to_name(m) for m in self._board.legal_moves()]

        
        if self.opening1() in legal_moves:
            move = self.opening1()
            print("I am playing an opening move: ", move)
            self._board.push(self._board.name_to_flat(move))
            return move

        if self.opening2() in legal_moves:
            move = self.opening2()
            print("I am playing an opening move: ", move)
            self._board.push(self._board.name_to_flat(move))
            return move

        if self.opening3() in legal_moves:
            move = self.opening3()
            print("I am playing an opening move: ", move)
            self._board.push(self._board.name_to_flat(move))
            return move
        
        # Check if a big move is available
        big_move = self.play_big_move()
        if big_move:
            return big_move


        # Set the maximum depth for the alpha-beta search
        max_depth = 10

        # Set the initial alpha and beta values
        alpha = float('-inf')
        beta = float('inf')

        # Set a time limit for the search
        start_time = time.time()
        time_limit = 5

        # If there is only one legal move, play it
        if len(legal_moves) == 1:
            move = legal_moves[0]
            print("I am playing ", move)
            self._board.push(self._board.name_to_flat(move))
            return move

        # Otherwise, use alpha-beta with iterative deepening to find the best move
        best_move = None
        for depth in range(1, max_depth + 1):
            current_best_move, current_best_score = self.alpha_beta(self._board, depth, alpha, beta, start_time, time_limit)
            if current_best_score is not None:
                best_move = current_best_move
                alpha = current_best_score
            if time.time() - start_time > time_limit:
                break

        self._board.push(self._board.name_to_flat(self._board.flat_to_name(best_move)))

        print("I am playing ", best_move)
        return self._board.flat_to_name(best_move)

    def alpha_beta(self, board, depth, alpha, beta, start_time, time_limit):
        best_move = None
        best_score = None
        for move in board.legal_moves():
            if time.time() - start_time > time_limit:
                break
            board.push(move)
            score = self.minimax(board, depth - 1, alpha, beta, False, start_time, time_limit)
            board.pop()
            if best_score is None or score > best_score:
                best_move = move
                best_score = score
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
        return best_move, best_score
    
    def minimax(self, board, depth, alpha, beta, is_maximizing_player, start_time, time_limit):
        if depth == 0 or board.is_game_over():
            return self.evaluate(board)

        if is_maximizing_player:
            max_score = float('-inf')
            for move in board.legal_moves():
                if time.time() - start_time > time_limit:
                    break
                board.push(move)
                score = self.minimax(board, depth - 1, alpha, beta, False, start_time, time_limit)
                board.pop()
                max_score = max(max_score, score)
                alpha = max(alpha, max_score)
                if beta <= alpha:
                    break
            return max_score
        else:
            min_score = float('inf')
            for move in board.legal_moves():
                if time.time() - start_time > time_limit:
                    break
                board.push(move)
                score = self.minimax(board, depth - 1, alpha, beta, True, start_time, time_limit)
                board.pop()
                min_score = min(min_score, score)
                beta = min(beta, min_score)
                if beta <= alpha:
                    break
            return min_score

    def liberties(self, board, color):
        visited = set()
        liberties = 0

        for i in range(board._BOARDSIZE):
            for j in range(board._BOARDSIZE):
                coord = board.flatten((i, j))
                if coord not in visited and board._board[coord] == color:
                    group, group_liberties = self.get_group_and_liberties(board, coord)
                    visited.update(group)
                    liberties += group_liberties

        return liberties

    def get_group_and_liberties(self, board, coord):
        group = set([coord])
        liberties = set()
        stack = [coord]
        color = board._board[coord]

        while stack:
            current = stack.pop()
            for neighbor in board._get_neighbors(current):
                if board._board[neighbor] == color and neighbor not in group:
                    group.add(neighbor)
                    stack.append(neighbor)
                elif board._board[neighbor] == Goban.Board._EMPTY:
                    liberties.add(neighbor)

        return group, len(liberties)

    def evaluate(self, board):
        '''
        Returns a score representing how advantageous the current board configuration is for the player
        with the given color. A positive score indicates an advantage for the player, and a negative score
        indicates a disadvantage.
        '''
        if board.is_game_over():
            winner = board.result()
            if winner == self._mycolor:
                return float("inf")
            elif winner == Goban.Board.flip(self._mycolor):
                return float("-inf")
            else:
                return 0

        # Calculate the scores
        scores = (self._board._nbBLACK, self._board._nbWHITE)

        # Calculate the number of legal moves for both players
        legal_moves_count = len(board.legal_moves())

        # Create a temporary copy of the board to switch perspectives
        temp_board = deepcopy(board)

        # Switch to the opponent's perspective and calculate the number of legal moves
        temp_board.play_move(-1)  # Pass move for the current player
        opponent_legal_moves_count = len(temp_board.legal_moves())

        # Calculate the number of liberties for both players
        my_liberties = self.liberties(board, self._mycolor)
        opponent_liberties = self.liberties(board, Goban.Board.flip(self._mycolor))

        # Calculate the evaluation score
        score_diff = scores[self._mycolor - 1] - scores[Goban.Board.flip(self._mycolor) - 1]
        legal_moves_diff = legal_moves_count - opponent_legal_moves_count
        liberties_diff = my_liberties - opponent_liberties
        evaluation_score = score_diff + legal_moves_diff + liberties_diff

        return evaluation_score

        
    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")



