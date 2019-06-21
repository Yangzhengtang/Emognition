#Aimed to transfer VGG model to a facial expression. But it was aborted because the accuracy is bad.
#Edited by Jiang Zhihao 
import keras
from keras.layers import Dense, Dropout, Activation, Flatten,Conv2D, MaxPooling2D
from keras.layers.normalization import BatchNormalization
from keras.models import Sequential,Model
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import EarlyStopping
from keras.optimizers import SGD
from keras import optimizers,applications
import numpy as np
import sys
import json
import time
import os
from keras.models import model_from_json

#Set value of the some parameter
image_size=48   #set the input image size as 48*48
base_model=applications.VGG16(weights='imagenet',include_top=False,input_shape=(48,48,1)) #load VGG16 as a base model to be transfer_trained
print('Model loaded')
origin_input_shape=1024 #VGG input shape 
train_num=2200 #num of train data
t_batch_size=32
epochs=50
usr_defined=2 #new num of categories
root_path = './pic/' 
trans_path='./trans_pic' #path of transfer learning dataset
model_path = root_path + 'model/'  # '/model_0.7/'
img_size = 48 #set the input image size as 48*48
emotion_labels = ['angry', 'disgust:', 'fear', 'happy', 'sad', 'surprise', 'neutral'] #label of original facial expression classifier
num_class = len(emotion_labels) 

#build transfer learning network part
top_model=Sequential() 
top_model.add(Flatten())
top_model.add(Dense(256,activation='relu',name='top_dense1'))
top_model.add(Dropout(0.5,name='new_dropout'))
top_model.add(Dense(usr_defined, activation='softmax',name='top_dense2'))
model=Model(inputs=base_model.input,outputs=top_model(base_model.output)) # connect the transfer learning network part and VGG part
for layer in model.layers[:15]: #freeze the first 15 layers
  layer.trainable=False

model.compile(loss='categorical_crossentropy',optimizer=optimizers.SGD(lr=1e-4,momentum=0.9),metrics=['accuracy'])#compile model

#to modify the dataset a little bit to expand the dataset
train_datagen = ImageDataGenerator(
    rescale = 1./255, 
    shear_range = 0.2,
    zoom_range = 0.2,
    horizontal_flip=True)#normalization
val_datagen = ImageDataGenerator(
       rescale = 1./255)
eval_datagen = ImageDataGenerator(
       rescale = 1./255)

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

early_stopping = EarlyStopping(monitor='loss',patience=3) #if the loss doesn't fall for 3 times, stop training
print(len(train_generator))

#history information
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

#save the model and structure
with open(trans_path+'/model_fit_log','w') as f:
    f.write(str(history_fit.history))
with open(trans_path+'/model_predict_log','w') as f:
    f.write(str(history_predict))

print('model trained')

json_file=open(model_path+"new_model_json.json", "w")#save weight and model
model_json=model.to_json()
json_file.write(model_json)
model.save_weights(model_path+'new_model_weight.h5')
model.save(root_path+'new_model.h5')
print('model saved')


