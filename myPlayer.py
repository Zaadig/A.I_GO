import numpy as np
from keras.models import load_model
from playerInterface import *
from Goban import Board
from random import choice

class myPlayer(PlayerInterface):
    def __init__(self):
        self._board = Board()
        self._mycolor = None
        self.model = load_model('my_op_model.h5') # Model trained on pro games, it tries to directly predict the best move

    def getPlayerName(self):
        return "Moulhanout"

    def get_state_for_nn(self, board): # Used to prepare board state for neural network
        state = np.zeros((board._BOARDSIZE, board._BOARDSIZE, 3), dtype=np.int8)
        for i in range(board._BOARDSIZE):
            for j in range(board._BOARDSIZE):
                coord = board.flatten((i, j))
                if board._board[coord] == self._mycolor:
                    state[i, j, 0] = 1
                elif board._board[coord] == Board.flip(self._mycolor):
                    state[i, j, 1] = 1
                else:
                    state[i, j, 2] = 1
        return state
    
    def getPlayerMove(self): 
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return "PASS"

        legal_moves = [self._board.flat_to_name(m) for m in self._board.legal_moves()]

        nn_input = self.get_state_for_nn(self._board) # Preparing the current state for the neural network

        nn_output = self.model.predict(np.expand_dims(nn_input, axis=0)) # Predicting the best move using the neural network
        nn_output = np.squeeze(nn_output, axis=0)

        # Finding the best move with the highest probability from the neural network output
        best_move = None
        best_probability = -1

        for move in legal_moves:
            i, j = Board.name_to_coord(move)
            probability = nn_output[i, j, 0]

            if probability > best_probability:
                best_move = move
                best_probability = probability

        print("I am playing ", best_move)
        self._board.push(Board.name_to_flat(best_move))
        return best_move


    def find_best_move_nn(self, legal_moves):  # Find the best move using the neural network
        board_state = self.get_state_for_nn(self._mycolor)

        predicted_moves = self.model.predict(np.array([board_state]))[0]

        best_score = None
        best_move = None

        for move in legal_moves:
            score = predicted_moves[self._board.flatten(move) // 2] # Calculate the score for the current move from predicted_moves
            if best_score is None or score > best_score:
                # If this is the first move or the current move has a better score, update the best_score and best_move 
                best_score = score
                best_move = move

        if best_move is None:
            best_move = choice(legal_moves)

        return best_move

    def playOpponentMove(self, move):
        self._board.push(self._board.name_to_flat(move))

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")
