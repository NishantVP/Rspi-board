#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import requests
import json
import datetime

# Init
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(40,GPIO.OUT)

continue_reading = True

# url = 'http://10.0.0.54:3000/attendance'
url = 'http://10.0.0.107:8080/IOTStanfordAttendanceSystem/stanford/attendance/markattendance/'
headers = {'Content-Type': 'application/json'}

# END Init

# Functions Def
def sendPOSTRequest(rfidTag):
    
    data = '''{"date":"07/05/2016","day":"wednesday","rfid":''' +str(rfidTag) +'''}'''
    print data
    response = requests.post(url, headers = headers ,data=data)
    print response

def sendGETRequest():
    print("Sending GET request...")
    response = requests.get(url, auth=('user', 'pass'))
    print response

def sendPUTRequest(rfidTag):
    # data = '''{"date":"07/05/2016","day":"wednesday","rfid":''' +str(rfidTag) +'''}'''
    data = str(rfidTag)
    print("Sending PUT request...")
    response = requests.put(url,data=data)
    print response


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# END Functions Def

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."


lastUID = ""
# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"

    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        currentUID = str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])

        if currentUID == lastUID:
            print "same card detected"
            time.sleep(1)
            print "UID Reset Success"
            lastUID = ""

        else:
            lastUID = currentUID
            # Print UID
            print "Card read UID: " +currentUID
            #+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])

            sendPUTRequest(currentUID);

            print "LED on"
            GPIO.output(40,GPIO.HIGH)
            time.sleep(1)
            # sendGETRequest()
            print "LED off"
            GPIO.output(40,GPIO.LOW)
            
            now = datetime.datetime.now()
            print str(now)
            # sendPOSTRequest(1)

            # This is the default key for authentication
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

            # Select the scanned tag
            MIFAREReader.MFRC522_SelectTag(uid)

            # Authenticate
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

            # Check if authenticated
            if status == MIFAREReader.MI_OK:
                MIFAREReader.MFRC522_Read(8)
                MIFAREReader.MFRC522_StopCrypto1()
            else:
                print "Authentication error"


