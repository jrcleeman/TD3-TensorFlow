import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Tensorflow version check
#print(tf.__version__) -> 2.7.0

#DNN Architecture
def build_and_compile_model(norm, size):
  model = keras.Sequential([
      norm,
      layers.Dense(128, activation='relu', input_shape = (size,)),
      layers.Dense(64, activation='relu'),
      layers.Dense(1, activation='tanh')
  ])

  model.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam(0.001))
  return model  

class ErrorDNN:
  def __init__(self, train = False):
    #Data Import
    self.importData()

    #NN Skeleton
    normalizer = tf.keras.layers.Normalization(input_dim=7, axis = -1) #Normalization Layer
    normalizer.adapt(np.array(self.train_features))
    size = self.train_features.shape[1]
    self.dnn_model = build_and_compile_model(normalizer, size) #Build DNN
    #print(self.dnn_model.summary()) #Print model architecture
    
    #Train or load model
    if train:
      self.train()
    else:
      self.loadModel()
    
    #Print side by side label comparison
    #self.printLineUp()

  def importData(self):
    '''Import Data'''
    column_names = ['FR_0', 'SS_0', 'LH_0', 'E_0', 'FR_1',
                    'SS_1', 'LH_1', 'E_1']

    fileName = "syntheticData.csv"
    raw_dataset = pd.read_csv(fileName, names=column_names, sep = ',')
    dataset = raw_dataset.copy()
    #print(dataset.tail()) #Print Last 5 Lines Check

    #Split into training and test sets
    train_dataset = dataset.sample(frac=0.8, random_state=0)
    test_dataset = dataset.drop(train_dataset.index)

    #Split features from labels
    self.train_features = train_dataset.copy()
    self.test_features = test_dataset.copy()
    self.train_labels = self.train_features.pop('E_1')
    self.test_labels = self.test_features.pop('E_1')      
  
  def train(self):
    history = self.dnn_model.fit(self.train_features, self.train_labels,
                            validation_split=0.2, verbose=2, 
                            epochs=110) #Train
    self.plot_loss(history) #Plot loss
    test_results = {}
    test_results['dnn_model'] = self.dnn_model.evaluate(self.test_features, self.test_labels, verbose=0)
    self.test_predictions = self.dnn_model.predict(self.test_features).flatten()
    #error = test_predictions - self.test_labels
    self.dnn_model.save('dnn_model.keras')

  def loadModel(self):
    self.dnn_model.load_weights('dnn_model.keras')
    #dnn_model = tf.keras.models.load_model('dnn_model.keras')
    self.test_predictions = self.dnn_model.predict(self.test_features).flatten()

  def printLineUp(self):
    lineup  = np.stack((np.array(self.test_labels), np.array(self.test_predictions)), axis=-1)
    for comparison in lineup:
      print(comparison)

  #Plot Loss
  def plot_loss(self, history):
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.xlabel('Epoch')
    plt.ylabel('Error')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
  train = False
  errorNN = ErrorDNN(train)