#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IA based covid19 test server

Created on Sat Mar 21 11:59:16 2020

@author: erickmfs
"""
###########LIBRERIAS/APIs/FRAMEWORKS##############
from tensorflow.keras.models import load_model
import numpy as np
import cv2

#import json
import paho.mqtt.client as mqtt

#import time

##########VARIABLES#############
data = []
labels = []
imagePath = "/home/erickmfs/ai_apps/covit19_vgg/keras-covid-19/dataset/normal/NORMAL2-IM-0696-0001.jpeg" #normal
modelpath = "/home/erickmfs/ai_apps/covit19_vgg/keras-covid-19/weights/covid19_vgg16_m2.h5"
MQTT_SERVER = "localhost"
#MQTT_PATH = "e1/cu_vol_po_samples"
MQTT_PATH = "cts/#"
NOMBRE_ESCLAVO = "cts"
COSTO_KWH = 0.6
working_mode = 0 #if 0: control mode, if 1: manual mode
topic_test = "cts/test"
#topic_nr_sw1 = "e1/utopico/sw1"
#topic_es = "e1/cu_vol_po_samples"
DIAG_CMD = "DIAG"
#CMD_SLV_ON = "ON"
#CMD_SLV_OFF = "OFF"
user = "cts"
password = "123456789cts"

###########FUNCTIONS###########
def get_np_image(imagePath):
    image = cv2.imread(imagePath)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (224, 224))
    
    image_in = np.array(image)/255.0
    image_input = image_in.reshape(1,224,224,3)
    # convert the data and labels to NumPy arrays while scaling the pixel
    # intensities to the range [0, 255]
    image_input = np.array(image_input) / 255.0
    #label = 1
    #label = np.array(label)
    return image_input

def get_diagnosis(modelpath, image_input):
    #'/home/erickmfs/ai_apps/covit19_vgg/keras-covid-19/weights/covid19_vgg16_m2.h5'
    model = load_model(modelpath)
    # make predictions on the testing set
    print("[INFO] evaluating network...")
    predIdxs = model.predict(image_input)
    # for each image in the testing set we need to find the index of the
    # label with corresponding largest predicted probability
    predIdxs = np.argmax(predIdxs, axis=1)    
    if predIdxs == 1:
        diagnostico = "NEGATIVO"        
    else:
        diagnostico = "POSITIVO"
    print("diagnostico:" + diagnostico)
        
    return diagnostico

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    print("()()()()()()---COVID19 TEST SERVER ONLINE---()()()()()()")
    #print(client + "/" + userdata + "/")
    #client.publish(topic_es,CMD_SLV_ON)
    #print("ON SENT")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)
    

def on_message(client, userdata, msg):
    topic = str(msg.topic)
    payload = str(msg.payload.decode('utf-8'))
    print("payload: " + payload)
    print("topic: " + topic)
    if topic == topic_test:
        imagepath = payload
        diag = get_diagnosis(modelpath, get_np_image(imagepath))
        #Diagnosis result is sent through mqtt
        client.publish(topic_test, diag)

#######INICIO DEL PROGRAMA#########
#mqtt connection
client = mqtt.Client()
#client = paho.Client()
client.username_pw_set(user, password)
#client.connect(“broker.mqttdashboard.com”)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)
#test of conection
client.publish(topic_test, "cts server connected")

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

