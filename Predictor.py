from tensorflow.keras.models import load_model
import numpy as np

board_size = 9

model = load_model('my_model.h5')

def name_to_coord(s):
    assert s != "PASS"
    indexLetters = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'F':5, 'G':6, 'H':7, 'J':8}

    col = indexLetters[s[0]]
    lin = int(s[1:]) - 1
    return col, lin

def raw_to_tensor(black_stones,white_stones):
    tensor = np.zeros((board_size,board_size,2))
    for i in range(len(black_stones)):
        x,y = name_to_coord(black_stones[i])[0],name_to_coord(black_stones[i])[1]
        tensor[x,y,0] = 1
        
    for i in range(len(white_stones)):
        x,y = name_to_coord(white_stones[i])[0],name_to_coord(white_stones[i])[1]
        tensor[x,y,1] = 1

    # Add padding to the tensor
    tensor = np.pad(tensor, pad_width=((1,1),(1,1),(0,0)), mode='constant')
    return tensor


def position_predict(black_stones, white_stones):

    tensor = raw_to_tensor(black_stones,white_stones)
    tensor = np.expand_dims(tensor, axis=0)
    prediction = model.predict(tensor)
    return prediction[0,0]


def predict_all(data):
    predicted_values = []
    
    for i in range(100):
        predicted_value = position_predict(data[i]["black_stones"], data[i]["white_stones"])
        true_value = data[i]["black_wins"] / data[i]["rollouts"]
        
        prediction = (predicted_value,true_value)
        predicted_values.append(prediction)
        print("predicted_value = {} - true_value = {}".format(predicted_value,true_value))
    
    return np.array(predicted_values)