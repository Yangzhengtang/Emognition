#Inorder to continuing training the tranfer model which is stopped before the train was completed
#Edite by Jiang Zhihao
import keras
from keras.layers import Dense, Dropout, Activation, Flatten,Conv2D, MaxPooling2D
from keras.layers.normalization import BatchNormalization
from keras.models import Sequential
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import EarlyStopping
from keras.optimizers import SGD
from keras import optimizers
import numpy as np
import sys
import json
import time
import os
from keras.models import load_model

#The following part is just the same as transfer_learning.py
#The only difference is the path name of model
origin_input_shape=1024
train_num=2200
t_batch_size=32
epochs=50
usr_defined=2
root_path = './pic/'
trans_path='./trans_pic'
model_path = root_path + 'model/'  # '/model_0.7/'
img_size = 48
emotion_labels = ['angry', 'disgust:', 'fear', 'happy', 'sad', 'surprise', 'neutral']
num_class = len(emotion_labels)

model=load_model('./pic/new_model.h5')
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
history_fit=model.fit_generator(
            train_generator,
            steps_per_epoch=train_num//epochs,
            epochs=epochs,
            validation_data=val_generator,
            validation_steps=40,
            )
history_predict=model.predict_generator(
            eval_generator,
            steps=40//epochs)
with open(trans_path+'/model_fit_log','w') as f:
    f.write(str(history_fit.history))
with open(trans_path+'/model_predict_log','w') as f:
    f.write(str(history_predict))
print('model trained')

json_file=open(model_path+"new_model_json2.json", "w")#save weight and model
model_json=model.to_json()
json_file.write(model_json)
model.save_weights(model_path+'new_model_weight2.h5')
model.save(root_path+'new_model2.h5')
print('model saved')
