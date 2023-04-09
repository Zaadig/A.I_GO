from tensorflow.keras.models import load_model
from myNeuralNetwork import raw_to_tensor
import numpy as np

model = load_model('my_model.h5')

def position_predict(black_stones, white_stones):

    tensor = raw_to_tensor(black_stones,white_stones)
    tensor = np.expand_dims(tensor, axis=0)
    prediction = model.predict(tensor)
    return prediction[0,0]


def predict_all(data):
    predicted_values = []
    
    for i in range(len(data)):
        tensor = raw_to_tensor(data[i]["black_stones"], data[i]["white_stones"])
        tensor = np.expand_dims(tensor, axis=0)
        predicted_value = model.predict(tensor)[0,0]
        true_value = data[i]["black_wins"] / data[i]["rollouts"]
        
        prediction = (predicted_value,true_value)
        predicted_values.append(prediction)
        print(prediction)
    
    return np.array(predicted_values)