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
        self.total_time_spent = 0

    def getPlayerName(self):
        return "Killer alpha-beta player"
    
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
        #the legal moves for the current player
        legal_moves = [self._board.flat_to_name(m) for m in self._board.legal_moves()]

        # Checking if any of the legal moves correspond to a big move
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

        # opening moves
        opening_move = self.play_opening_move()
        if opening_move:
            return opening_move

        # Checking if a big move is available
        big_move = self.play_big_move()
        if big_move:
            return big_move

        max_depth = 10
        time_limit = 60

        start_time = time.time()

        best_move = None
        for depth in range(1, max_depth + 1):
            current_best_move, current_best_score = self.alpha_beta(self._board, depth, float('-inf'), float('inf'), start_time, time_limit)
            if current_best_score is not None:
                best_move = current_best_move
            if time.time() - start_time > time_limit:
                break

        self._board.push(self._board.name_to_flat(self._board.flat_to_name(best_move)))
        print("I am playing ", best_move)
        return self._board.flat_to_name(best_move)

    def play_opening_move(self):
        legal_moves = [self._board.flat_to_name(m) for m in self._board.legal_moves()]
        for opening in (self.opening1, self.opening2, self.opening3):
            move = opening()
            if move in legal_moves:
                print("I am playing an opening move: ", move)
                self._board.push(self._board.name_to_flat(move))
                return move
        return None

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
            return self.ImprovedEvaluation(board)

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
                coord = Goban.Board.flatten((i, j))
                if coord not in visited and board._board[coord] == color:
                    group, group_liberties = self.get_group_and_liberties(board, (i,j))
                    visited.update(group)
                    liberties += len(group_liberties)

        return liberties
  
    def ImprovedEvaluation(self,board):
        if board.is_game_over():
            winner = board.result()
            if winner == self._mycolor:
                return float("inf")
            elif winner == Goban.Board.flip(self._mycolor):
                return float("-inf")
            else:
                return 0

        scores = (self._board._nbBLACK, self._board._nbWHITE)
        score_diff = scores[self._mycolor - 1] - scores[Goban.Board.flip(self._mycolor) - 1]

        legal_moves_count = len(board.legal_moves())
        temp_board = deepcopy(board)
        temp_board.play_move(-1)
        opponent_legal_moves_count = len(temp_board.legal_moves())
        legal_moves_diff = legal_moves_count - opponent_legal_moves_count

        my_liberties = self.liberties(board, self._mycolor)
        opponent_liberties = self.liberties(board, Goban.Board.flip(self._mycolor))
        liberties_diff = my_liberties - opponent_liberties

        my_groups = self.get_groups(board, self._mycolor)
        my_group_liberties = [len(liberties) for group, liberties in my_groups]
        opponent_groups = self.get_groups(board, Goban.Board.flip(self._mycolor))
        opponent_group_liberties = [len(liberties) for group, liberties in opponent_groups]


        groups_diff = len(my_groups) - len(opponent_groups)
        group_liberties_diff = sum(my_group_liberties) - sum(opponent_group_liberties)

        my_influence = self.calculate_influence(board, self._mycolor)
        opponent_influence = self.calculate_influence(board, Goban.Board.flip(self._mycolor))
        influence_diff = my_influence - opponent_influence

        if self._mycolor == Goban.Board._WHITE:
            captured_diff = board._capturedWHITE - board._capturedBLACK
        else:
            captured_diff = board._capturedBLACK - board._capturedWHITE


        # Assigning weights to the different factors, kind of arbitrary
        w_score = 10
        w_legal_moves = 3
        w_liberties = 1
        w_groups = 2
        w_group_liberties = 5
        w_influence = 4
        w_captured = 2

        evaluation_score = (
            w_score * score_diff +
            w_legal_moves * legal_moves_diff +
            w_liberties * liberties_diff +
            w_groups * groups_diff +
            w_group_liberties * group_liberties_diff +
            w_influence * influence_diff +
            w_captured * captured_diff
        )

        return evaluation_score

    def calculate_influence(self, board, color):
        influence_board = [[0] * board._BOARDSIZE for _ in range(board._BOARDSIZE)]

        for x in range(board._BOARDSIZE):
            for y in range(board._BOARDSIZE):
                pos = (x, y)
                fpos = Goban.Board.flatten(pos) 
                if board.__getitem__(fpos) == color:
                    for nx in range(board._BOARDSIZE):
                        for ny in range(board._BOARDSIZE):
                            dist = abs(nx - x) + abs(ny - y)
                            influence_board[nx][ny] += 1 / (dist + 1)

        total_influence = sum(sum(row) for row in influence_board)
        return total_influence


    def get_groups(self, board, color):
        visited = set()
        groups = []

        for x in range(board._BOARDSIZE):
            for y in range(board._BOARDSIZE):
                pos = (x, y)
                fpos = Goban.Board.flatten(pos) 
                if pos not in visited and board.__getitem__(fpos) == color:
                    group, liberties = self.get_group_and_liberties(board, pos)
                    groups.append((group, liberties))
                    visited.update(group)

        return groups


    def get_group_and_liberties(self, board, pos):
        group = set()
        liberties = set()
        stack = [pos]
        fpos = Goban.Board.flatten(pos)
        color = board.__getitem__(fpos)

        while stack:
            x, y = stack.pop()
            group.add((x, y))

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < board._BOARDSIZE and 0 <= ny < board._BOARDSIZE:
                    npos = (nx, ny)
                    fnpos = Goban.Board.flatten(npos)
                    if board.__getitem__(fnpos) == color and npos not in group:
                        stack.append(npos)
                    elif board.__getitem__(fnpos) == Goban.Board._EMPTY:
                        liberties.add(npos)

        return group, liberties



        
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



