# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 14:22:19 2019

@author: rashedi
"""

import os
import zipfile
import numpy as np
local_zip='Datasets\dogs-vs-cats.zip'
zipref=zipfile.ZipFile(local_zip,'r')
zipref.extractall('Datasets\dogs-vs-cats')
zipref.close()

categories=[]
filenames=os.listdir('Datasets/dogs-vs-cats/train')
for filename in filenames:
    if filename.split('.')[0]=='cat':
        categories.append(0)
    else:
        categories.append(1)
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, ImageDataGenerator
import pandas as pd
df_train=pd.DataFrame({'File Name':filenames, 'Label':categories})
df_train.head()

model=tf.keras.models.Sequential([tf.keras.layers.Conv2D(16,(3,3),activation='relu',input_shape=(128,128,3)),
                                                         tf.keras.layers.BatchNormalization(),
                                                         tf.keras.layers.MaxPooling2D(2,2),
                                                         tf.keras.layers.Dropout(0.25),
                                                         tf.keras.layers.Conv2D(32,(3,3),activation='relu'),
                                                          tf.keras.layers.BatchNormalization(),
                                                         tf.keras.layers.MaxPooling2D(2,2),
                                                          tf.keras.layers.Dropout(0.25),
                                                         tf.keras.layers.Conv2D(64,(3,3),activation='relu'),
                                                          tf.keras.layers.BatchNormalization(),
                                                         tf.keras.layers.MaxPooling2D(2,2),
                                                          tf.keras.layers.Dropout(0.25),
                                                         tf.keras.layers.Conv2D(128,(3,3),activation='relu'),
                                                          tf.keras.layers.BatchNormalization(),
                                                         tf.keras.layers.MaxPooling2D(2,2),
                                                          tf.keras.layers.Dropout(0.25),
                                                         tf.keras.layers.Flatten(),
                                                         tf.keras.layers.Dense(256,activation='relu'),
                                                         tf.keras.layers.Dense(1,activation='sigmoid')])
model.compile(loss='binary_crossentropy',metrics=['acc'],optimizer='adam')

from sklearn.model_selection import train_test_split
class mycallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self,epoch,logs={}):
        if logs.get('acc')>0.85:
            print('\nReached 85% accuracy, so please stop training!')
            self.model.stop_training=True
callback=mycallback()
df_train['Label']=df_train['Label'].replace({0:'cat',1:'dog'})

train_df,validation_df=train_test_split(df_train,test_size=0.2,random_state=42)

train_datagen=ImageDataGenerator(rotation_range=15,rescale=1/255,shear_range=0.1,zoom_range=0.2,horizontal_flip=True,width_shift_range=0.1,height_shift_range=0.1)
train_generator=train_datagen.flow_from_dataframe(train_df,'Datasets/dogs-vs-cats/train',x_col='File Name',y_col='Label',target_size=(128,128),class_mode='binary',batch_size=16)
validation_datagen=ImageDataGenerator(rotation_range=15,rescale=1/255,shear_range=0.1,zoom_range=0.2,horizontal_flip=True,width_shift_range=0.1,height_shift_range=0.1)
validation_generator=validation_datagen.flow_from_dataframe(validation_df,'Datasets/dogs-vs-cats/train',x_col='File Name',y_col='Label',target_size=(128,128),class_mode='binary',batch_size=16)

history=model.fit_generator(train_generator,epochs=10,validation_data=validation_generator,steps_per_epoch=train_df.shape[0]/16,validation_steps=validation_df.shape[0]/16,callbacks=[callback])

model.save_weights('cat_dog_weights.h5')

import matplotlib.pyplot as plt
fig,(ax1,ax2)=plt.subplots(2,1,figsize=(12,12))
ax1.plot(history.history['loss'],color='b',label='Train')
ax1.plot(history.history['val_loss'],color='r',label='Validation')
plt.ylabel('Loss')
plt.xlabel('Epoch')
ax2.plot(history.history['acc'],color='b',label='Train')
ax2.plot(history.history['val_acc'],color='r',label='Validation')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(loc='best',shadow=True)
plt.tight_layout()

test_names=os.listdir('Datasets/dogs-vs-cats/test')
df_test=pd.DataFrame({'Name':test_names})
df_test.shape[0]

test_datagen=ImageDataGenerator(rescale=1/255)
test_generator=test_datagen.flow_from_dataframe(df_test,'Datasets/dogs-vs-cats/test',x_col='Name',y_col=None,target_size=(128,128),batch_size=16,class_mode=None)
predicted=model.predict_generator(test_generator,steps=np.round(df_test.shape[0]/16))

predict_categ=[]
for i in range(len(predicted)):
    if predicted[i]>=0.5:
        predict_categ.append(1)
    else:
        predict_categ.append(0)
df_test['Label']=predict_categ