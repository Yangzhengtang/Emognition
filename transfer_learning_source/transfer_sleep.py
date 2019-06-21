#Aimed to transfer basic facial expression detect model to a 'sleep or not' 
#Edited by Jiang Zhihao 
import keras
from keras.layers import Dense, Dropout, Activation, Flatten,Conv2D, MaxPooling2D
from keras.layers.normalization import BatchNormalization
from keras.models import Sequential
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import EarlyStopping
from keras.optimizers import SGD
from keras import optimizers
#from keras.models import load_weights
import numpy as np
import sys
import json
import time
import os
# import copy
from keras.models import model_from_json


#Set value of the some parameter
origin_input_shape=1024 #original model input shape
train_num=295 #num of train data
t_batch_size=32
epochs=10
usr_defined=2 #new num of categories
root_path = './pic/'
trans_path='./sleep_trans' #path of transfer learning dataset
model_path = root_path + 'model/'  # '/model_0.7/'
img_size = 48 #set the input image size as 48*48
emotion_labels = ['angry', 'disgust:', 'fear', 'happy', 'sad', 'surprise', 'neutral'] #label of original facial expression classifier
num_class = len(emotion_labels)	
json_file = open(model_path + 'model_json.json') 
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)#load basic model structure
print(len(model.layers))

#Edit the basic model, pop the original classifier layers
model.pop()
model.pop()
model.pop()
model.pop()
model.pop()
model.pop()
model.pop()
model.pop()
model.pop()
print(len(model.layers))

#Edit the basic model, add new classifier layers.
model.add(Flatten())
model.add(Dense(256,activation='relu',name='top_dense1'))
model.add(Dropout(0.5,name='new_dropout'))
model.add(Dense(usr_defined, activation='softmax',name='top_dense2'))
print(len(model.layers))#rebuild model done
for layer in model.layers[:11]: #freeze the first 11 layers
  layer.trainable=False
model.load_weights(model_path + 'model_weight.h5',by_name=True)#load original weight
model.compile(loss='categorical_crossentropy',optimizer=optimizers.SGD(lr=1e-4,momentum=0.9),metrics=['accuracy'])#compile model

#to modify the dataset a little bit to expand the dataset
train_datagen = ImageDataGenerator(
    rescale = 1./255,
    shear_range = 0.2,
    zoom_range = 0.2,
    horizontal_flip=True)
    #normalization
val_datagen = ImageDataGenerator(
       rescale = 1./255)
eval_datagen = ImageDataGenerator(
       rescale = 1./255)
    #label based on file name

#load the traindata
train_generator = train_datagen.flow_from_directory(
            trans_path+'/train',
            target_size=(img_size,img_size),
            color_mode='grayscale',
            batch_size=t_batch_size,
            class_mode='categorical')
val_generator = val_datagen.flow_from_directory(
            trans_path+'/val',
            target_size=(img_size,img_size),
            color_mode='grayscale',
            batch_size=t_batch_size,
            class_mode='categorical')
eval_generator = eval_datagen.flow_from_directory(
            trans_path+'/test',
            target_size=(img_size,img_size),
            color_mode='grayscale',
            batch_size=t_batch_size,
            class_mode='categorical')
early_stopping = EarlyStopping(monitor='loss',patience=3)
print(len(train_generator))

#history information
history_fit=model.fit_generator(
            train_generator,
            steps_per_epoch=200,
            epochs=epochs,
            validation_data=val_generator,
            validation_steps=40,
            )

#save the model and structure
history_predict=model.predict_generator(
            eval_generator,
            steps=40//epochs)
with open(trans_path+'/model_fit_log','w') as f:
    f.write(str(history_fit.history))
with open(trans_path+'/model_predict_log','w') as f:
    f.write(str(history_predict))
print('model trained')
json_file=open(model_path+"sleep_model_json.json", "w")#save weight and model
model_json=model.to_json()
json_file.write(model_json)
model.save_weights(model_path+'sleep_model_weight.h5')
model.save(root_path+'sleep_model.h5')
print('model saved')


