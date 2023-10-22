import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Tensorflow version check
#print(tf.__version__) -> 2.7.0

def plot_loss(history):
  plt.plot(history.history['loss'], label='loss')
  plt.plot(history.history['val_loss'], label='val_loss')
  #plt.ylim([0, 10])
  plt.xlabel('Epoch')
  plt.ylabel('Error')
  plt.legend()
  plt.grid(True)
  plt.show()

'''Import Data'''
column_names = ['FR_0', 'SS_0', 'LH_0', 'E_0', 'FR_1',
                'SS_1', 'LH_1', 'E_1']

fileName = "syntheticData.csv"
raw_dataset = pd.read_csv(fileName, names=column_names, sep = ',')
dataset = raw_dataset.copy()
print(dataset.tail()) #Print Last 5 Lines Check

#Split into training and test sets
train_dataset = dataset.sample(frac=0.8, random_state=0)
test_dataset = dataset.drop(train_dataset.index)

#Split features from labels
train_features = train_dataset.copy()
test_features = test_dataset.copy()
train_labels = train_features.pop('E_1')
test_labels = test_features.pop('E_1')

'''DNN'''
#Normalize Features
#print(train_dataset.describe().transpose()[['mean', 'std']]) #Print Mean and Std of each column
normalizer = tf.keras.layers.Normalization(input_dim=7, axis = -1) #Normalization Layer
normalizer.adapt(np.array(train_features))

#DNN Architecture
def build_and_compile_model(norm, size):
  model = keras.Sequential([
      norm,
      layers.Dense(128, activation='relu', input_shape = (size,)),
      layers.Dense(64, activation='relu'),
      layers.Dense(1, activation='tanh')
  ])

  model.compile(loss='mean_squared_error',
                optimizer=tf.keras.optimizers.Adam(0.001))
  return model

'''Train'''
train = True
size = train_features.shape[1]
if train:
    
    dnn_model = build_and_compile_model(normalizer, size) #Build DNN
    print(dnn_model.summary()) #Print model architecture
    history = dnn_model.fit(train_features, train_labels,
                             validation_split=0.2, verbose=2, 
                             epochs=110) #Train
    plot_loss(history) #Plot loss
    test_results = {}
    test_results['dnn_model'] = dnn_model.evaluate(test_features, test_labels, verbose=0)
    test_predictions = dnn_model.predict(test_features).flatten()
    error = test_predictions - test_labels
    dnn_model.save('dnn_model.keras')

else:
    dnn_model = build_and_compile_model(normalizer, size)
    dnn_model.load_weights('dnn_model.keras')
    #dnn_model = tf.keras.models.load_model('dnn_model.keras')
    test_predictions = dnn_model.predict(test_features).flatten()

lineup  = np.stack((np.array(test_labels), np.array(test_predictions)), axis=-1)
for comparison in lineup:
   print(comparison)