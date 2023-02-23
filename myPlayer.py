# -*- coding: utf-8 -*-
''' This is the file you have to modify for the tournament. Your default AI player must be called by this module, in the
myPlayer class.

Right now, this class contains the copy of the randomPlayer. But you have to change this!
'''

import time
import Goban 
from random import choice
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
        return "Player ma hrbanch"

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS" 
            
        # Set the maximum depth for the alpha-beta search
        max_depth = 3
        
        # Set the initial alpha and beta values
        alpha = float('-inf')
        beta = float('inf')
        
        # Get the legal moves for the current player
        legal_moves = [self._board.flat_to_name(m) for m in self._board.legal_moves()]
        
        # If there is only one legal move, play it
        if len(legal_moves) == 1:
            move = legal_moves[0]
            print("I am playing ", move)
            self._board.push(self._board.name_to_flat(move))
            return move
        
        # Otherwise, use alpha-beta to find the best move
        best_move = None
        best_score = float('-inf')
        for move in legal_moves:
            self._board.push(self._board.name_to_flat(move))
            score = self.alpha_beta(self._board, max_depth, alpha, beta, False)
            self._board.pop()
            if score > best_score:
                best_move = move
                best_score = score
            alpha = max(alpha, best_score)
        self._board.push(self._board.name_to_flat(best_move))
        print("I am playing ", best_move)
        return best_move

    def alpha_beta(self, board, depth, alpha, beta, is_maximizing_player):
        if depth == 0 or board.is_game_over():
            return self.evaluate(board)
        if is_maximizing_player:
            max_score = float('-inf')
            for move in board.legal_moves():
                board.push(move)
                score = self.alpha_beta(board, depth - 1, alpha, beta, False)
                board.pop()
                max_score = max(max_score, score)
                alpha = max(alpha, max_score)
                if beta <= alpha:
                    break
            return max_score
        else:
            min_score = float('inf')
            for move in board.legal_moves():
                board.push(move)
                score = self.alpha_beta(board, depth - 1, alpha, beta, True)
                board.pop()
                min_score = min(min_score, score)
                beta = min(beta, min_score)
                if beta <= alpha:
                    break
            return min_score

    def evaluate(self,board):
        '''
        Returns a score representing how advantageous the current board configuration is for the player
        with the given color. A positive score indicates an advantage for the player, and a negative score
        indicates a disadvantage.
        '''
        # Check if the game is over and return a large score if it is.
        if board.is_game_over():
            winner = board.result()
            if winner == self._mycolor:
                return float("inf")
            elif winner == Goban.Board.flip(self._mycolor):
                return float("-inf")
            else:
                return 0

        # Calculate the difference in score between the two players.
        scores = (self._board._nbBLACK , self._board._nbWHITE)
        score_diff = scores[self._mycolor -1] - scores[Goban.Board.flip(self._mycolor) -1]
        return score_diff



        
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



