import numpy as np
import pickle
from keras.models import Sequential
from keras.layers import Conv2D, Dense, Flatten, BatchNormalization, Dropout
from keras.optimizers import Adam
from keras.losses import CategoricalCrossentropy
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.layers import Reshape

# Load the preprocessed data
with open("train_set.pickle", "rb") as f:
    train_set = pickle.load(f)

with open("val_set.pickle", "rb") as f:
    val_set = pickle.load(f)

with open("test_set.pickle", "rb") as f:
    test_set = pickle.load(f)

# Extract the input (X) and output (y) data
def extract_X_y(dataset):
    X, y = [], []
    for _, _, _, _, moves in dataset:
        for i in range(len(moves) - 1):
            X.append(moves[i])
            y.append(moves[i + 1][:, :, :2])
    return np.array(X), np.array(y)

X_train, y_train = extract_X_y(train_set)
X_val, y_val = extract_X_y(val_set)
X_test, y_test = extract_X_y(test_set)

# Build the neural network
model = Sequential([
    Conv2D(32, kernel_size=3, activation='relu', padding='same', input_shape=(9, 9, 3)),
    BatchNormalization(),
    Conv2D(32, kernel_size=3, activation='relu', padding='same'),
    BatchNormalization(),
    Dropout(0.5),
    Flatten(),
    Dense(64, activation='relu'),
    BatchNormalization(),
    Dense(9 * 9 * 2, activation='softmax'),
    Reshape((9, 9, 2)), 
])

# Compile the model
model.compile(optimizer=Adam(learning_rate=0.001), loss=CategoricalCrossentropy(), metrics=['accuracy'])

# Train the neural network
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=1e-5)
history = model.fit(X_train, y_train, epochs=2, batch_size=64, validation_data=(X_val, y_val), callbacks=[early_stopping, reduce_lr], verbose=1)

# Test the neural network
test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
print(f"Test loss: {test_loss}")
print(f"Test accuracy: {test_accuracy}")

model.save('my_op_model.h5')
