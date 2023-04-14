import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Dropout,Flatten
from keras.layers import Conv2D, BatchNormalization,LeakyReLU
from keras.callbacks import Callback
from keras.callbacks import EarlyStopping
from keras import metrics
import keras.optimizers as optimizers
import gzip, os
import json
import pickle
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit


# ------------------------------------------------------ INITIAL DATA ------------------------------------------------------------------------------------------------------


def get_raw_data_go():
    ''' Returns the set of samples from the local file or download it if it does not exists'''
    
    raw_samples_file = "samples-9x9.json.gz"

    if not os.path.isfile(raw_samples_file):
        print("File", raw_samples_file, "not found, I am downloading it...", end="")
        import urllib.request 
        urllib.request.urlretrieve ("https://www.labri.fr/perso/lsimon/static/inge2-ia/samples-9x9.json.gz", "samples-9x9.json.gz")
        print(" Done")

    with gzip.open("samples-9x9.json.gz") as fz:
        data = json.loads(fz.read().decode("utf-8"))
    return data

data = get_raw_data_go()


# ----------------------------------------------------DATA PREPARATION------------------------------------------------------------------------------------------------------

board_size = 9


# This function takes a string that represents a position on a Go board, such as "A1" or "J9",
#  and converts it to a tuple of coordinates in the form (column, row).
def name_to_coord(s):
    assert s != "PASS"
    indexLetters = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'J':8}

    col = indexLetters[s[0]]
    lin = int(s[1:]) - 1
    return col, lin


# This function takes lists of black and white stones on a Go board, and returns a tensor that represents the state of the board. 
# The tensor is a 3D NumPy array with shape (2, 9, 9), 
# where the first dimension represents black and white stones, and the second and third dimensions represent the rows and columns of the board
def raw_to_tensor(black_stones,white_stones):
    tensor = np.zeros((board_size,board_size,2))
    for i in range(len(black_stones)):
        x,y = name_to_coord(black_stones[i])[0],name_to_coord(black_stones[i])[1]
        tensor[x,y,0] = 1
        
    for i in range(len(white_stones)):
        x,y = name_to_coord(white_stones[i])[0],name_to_coord(white_stones[i])[1]
        tensor[x,y,1] = 1

    tensor = np.pad(tensor, pad_width=((1,1),(1,1),(0,0)), mode='constant') # Add padding to the tensor
    return tensor


# This function takes a tensor that represents a set of Go board states and applies symmetries to it in order to increase the size of the dataset. 
# The symmetries include rotations and flips of the board, as well as rotations and flips of the colors (i.e. swapping black and white). 
# The resulting tensor has shape (8 * original_size, 2, 11, 11), .
def expand_dataset(data_tensor):

    size = data_tensor.shape[0]   # Get the size of the original dataset

    expanded_data_tensor = np.zeros((size*8, board_size+2, board_size+2, 2)) # Create a new tensor to hold the expanded dataset

    expanded_data_tensor[0:size] = data_tensor # Copy the original data to the expanded tensor

    # This is where the data is expanded using symmetries
    for rot in range(1, 4):
        for idx in range(size):
            expanded_data_tensor[rot*size + idx, :, :, 0] = np.rot90(expanded_data_tensor[(rot-1)*size + idx, :, :, 0])
            expanded_data_tensor[rot*size + idx, :, :, 1] = np.rot90(expanded_data_tensor[(rot-1)*size + idx, :, :, 1])

    for mirror in range(4, 8):
        for idx in range(size):
            expanded_data_tensor[mirror*size + idx, :, :, 0] = np.flipud(expanded_data_tensor[(mirror-4) * size + idx, :, :, 0])
            expanded_data_tensor[mirror*size + idx, :, :, 1] = np.flipud(expanded_data_tensor[(mirror-4) * size + idx, :, :, 1])

    return expanded_data_tensor

data_tensor = np.zeros((len(data), board_size+2, board_size+2, 2))
for i in range(len(data)):
    black_stones = data[i]['black_stones']
    white_stones = data[i]['white_stones']
    data_tensor[i] = raw_to_tensor(black_stones, white_stones)

print("data size before expansion:",data_tensor.shape)

data_tensor = expand_dataset(data_tensor)

print("data size after expansion:",data_tensor.shape)

y = np.array([(data[i]["black_wins"]/data[i]["rollouts"], data[i]["white_wins"]/data[i]["rollouts"]) for i in range(len(data))])

y = np.concatenate((y, y, y, y, y, y, y, y))

# create an array of labels based on the proportion of black and white wins
labels = np.argmax(y, axis=1)

# --------------------------------------------------- DIVIDING DATA into training,validation and test data -----------------------------------------------------------------------------------------------------------


# create an array of labels based on the proportion of black and white wins
labels = np.argmax(y, axis=1)

# create a StratifiedShuffleSplit object with the desired parameters
sss = StratifiedShuffleSplit(n_splits=1, test_size=0.33, random_state=42)

# use the object to split the data into train and test sets while preserving the label proportions
for train_index, test_index in sss.split(data_tensor, labels):
    X_train, X_test = data_tensor[train_index], data_tensor[test_index]
    y_train, y_test = y[train_index], y[test_index]

# create a new StratifiedShuffleSplit object to split the remaining data into validation and holdout sets
sss2 = StratifiedShuffleSplit(n_splits=1, test_size=0.5, random_state=42)

# use the object to split the data into validation and holdout sets while preserving the label proportions
for val_index, holdout_index in sss2.split(X_test, np.argmax(y_test, axis=1)):
    X_val, X_holdout = X_test[val_index], X_test[holdout_index]
    y_val, y_holdout = y_test[val_index], y_test[holdout_index]


# ---------------------------------------------------- MODEL -------------------------------------------------------------------------------------------------------



model = Sequential()

model.add(Conv2D(filters=64, kernel_size=(3, 3), activation='relu', padding='same', input_shape=(board_size+2, board_size+2, 2)))
model.add(Conv2D(filters=32, kernel_size=(2, 2), activation='relu'))
model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(2, activation='sigmoid'))

model.compile(loss='mse', optimizer='adam', metrics=['accuracy', 'mae', 'mse'])

# Define a custom callback to track training history
class History(Callback):
    def __init__(self):
        self.history = {}
    
    def on_epoch_end(self, epoch, logs={}):
        # Add the current epoch's metrics to the history dictionary
        for k,v in logs.items():
            if not k in self.history: self.history[k]=[]
            self.history[k].append(v)
        print(".",end="")

history=[History()]

model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=30, batch_size=64, callbacks=history)

model.summary()

score = model.evaluate(X_test, y_test, verbose=0)
print('Test loss:', score)

model.save('my_model.h5')



# ------------------------------------------------------------------ END -----------------------------------------------------------------------------------------



