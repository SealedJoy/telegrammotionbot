#!/usr/bin/env python
# -*- coding: utf-8 -*-
### OpSpot Camera Bot ###
### by Joseph Slade ###
### 26th Jan 2019 ###
# contact sealedjoy@gmail.com #
#
# Logs @ logs/python.log
#
## Version Number ##
releaseversion = 0.1
## Version Number ##
#
# Begin Libraries #
#-----------------#
import emoji # easy referencing of emoji see http://www.unicode.org/emoji/charts/full-emoji-list.html
import configparser # Import from configuration.ini
import threading # Stay responsive - Threads for tasks
from queue import Queue
import requests # Get camera stream image
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters 
import logging
import inotify.adapters
import os
import re
import random
import json
import ffmpy
import subprocess
import telegram
import time
from time import gmtime, strftime
import datetime as dt
import sys
from threading import Thread
import signal
# End Libraries #
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)
# Handle Exitcodes (0) with sigterm / ctrl + c
signal.signal(signal.SIGINT, signal_handler)

# Threads and queue setup ##########
#~ print_lock = threading.Lock()

#~ def exampleJob(worker):
    #~ time.sleep(0.5)
    
    #~ with print_lock:
        #~ print(threading.current_thread().name, worker)
        
#~ def threader():
    #~ while True:
        #~ worker = q.get()
        #~ exampleJob(worker)
        #~ q.task_done()

#~ q = Queue()
#~ for x in range(10):
    #~ t = threading.Thread(target = threader)
    #~ t.daemon = True
    #~ t.start()
    
#~ start = time.time()
#~ for worker in range (20):
    #~ q.put(worker)
    
#~ q.join()
#~ print('entire job took: ', time.time() - start)
####################### END QUEUE SETUP 

# Import config file and set values #
config = configparser.ConfigParser()
config.read('/home/pi/scripts/updateopspot/config/configuration.ini')
confUser = config['USER']
confCam = config['CAMERA'] 
confPackage = config['PACKAGE'] 

# Check to see if new version of script
checkversion = float(confPackage['Version'])
scriptupdatedflag = False
if checkversion < releaseversion:
    scriptupdatedflag = True
    scriptdowngraded = False
    config['PACKAGE']['Updated'] = strftime("%Y-%m-%d", gmtime())
elif checkversion > releaseversion:
    scriptupdatedflag = True
    scriptdowngraded = True
    config['PACKAGE']['Updated'] = strftime("%Y-%m-%d", gmtime())

### TELEGRAM 
CamName = confCam['CameraName']
image_url = confCam['SnapshotUrl']

# Authentication Token from BotFather
TOKEN = confUser['authkey']
# Telegram Username of Owner
user = confUser['user']
# Telegram User Chat ID
chatid = confUser['chatid']
# Set Bot Initially - needed for unprompted updates
bot = telegram.Bot(token = TOKEN)
# Get bot name and save to config
#confBot = config['BOT']
#namebot = confBot['bot']
botname = str(bot.get_me())
#print(botname)
#jsonbot = json.loads(bot)
config['BOT']['Bot'] = botname
config['PACKAGE']['Version'] = str(releaseversion)

sendallvideos = config['TELEGRAM'].getboolean('SendAll')
rcloneupload = config['CLOUD'].getboolean('Upload')
shownotificatons = config['TELEGRAM'].getboolean('Notifications')
motionbool = config['CAMERA'].getboolean('Motion')
watched_folder = confCam['CamMediaRootDir']

# Vars for update checking
updateflaglocation='/home/pi/scripts/updateopspot/check/flag'
scriptpath='/home/pi/scripts/opspot/python-telegram-bot.py'
downloadscriptpath='/home/pi/scripts/updateopspot/check/python-telegram-bot.py'
downloadscriptfolder='/home/pi/scripts/updateopspot/check'

# Vars for toggle single messages on changing /photo source
switched2stream = False
switched2local = False
first_record_msg = True

# Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='/home/pi/scripts/updateopspot/logs/python.log', level=logging.INFO) # change logging.INFO to DEBUG for verbose logging 
logging.basicConfig()
logging.info('Started')
print ("started Log")

print(r"""
---------------------------------------
                """) 
                
print ("Settings:")
print ("- Telegram Bot is: "),
printbotname = ""
for x in range(15,30):
    if botname[x] == "'":
        break
    else:
        printbotname = printbotname + botname[x]
print(printbotname)
print ("- Owner is: " + user)
print ("- Watching: " + watched_folder)
print ("- Upload to Cloud: " + str(rcloneupload))
print ("- Google Drive Folder: " + "/" + CamName)
print ("- Notificatons: " + str(shownotificatons))
print ("- Send All Videos (Telegram): " + str(sendallvideos))
print ("- Motion Detection: " + str(motionbool))
print ("- Snapshot URL: " + image_url)

logging.info("Config:")
logging.info("--------------")
logging.info("Telegram Bot is: " + printbotname)
logging.info("Watching: " + watched_folder)
logging.info("Upload to Cloud: " + str(rcloneupload))
logging.info("Google Drive Folder: " + "/" + CamName)
logging.info("Notificatons: " + str(shownotificatons))
logging.info("Motion Detection: " + str(motionbool))
logging.info("Send All Videos (Telegram): " + str(sendallvideos))
logging.info("Snapshot URL: " + image_url)
print(r"""
---------------------------------------
                """) 
print(r"""
        IOT Bot Security System

                  \ | /
                 '  _  '
                -  |_|  -
                 ' | | '
                 _,_|___
                |   _ []|
                |  (O)  |
                |_______|
        
      All rights reserved J. Slade 2019
   ---------------------------------------
            sealedjoy@gmail.com
             telegram: @Sealyj
                """)
print ("\n")

print(r"""
---------------------------------------
                """) 

                

audio_path = 'media/recording1.wav'
photo_path = 'media/nophoto.gif'
file_path = 'media/novideo.mp4'
file_name = 'novideo.mp4'
filesize = 0
switched2stream = False
switched2local = False
#globalbot = {'username': u'SHCamBot', 'first_name': u'SHCamBot', 'id': 763940967} was like that should have quotes "{'user' : 'sgsdg' } "





def systemcommand(command):
    try:
        print("starting subprocess: " + str(command))
        res = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE);
        output,error = res.communicate()
        if output:
            print "ret> ",res.returncode
            print "OK> output ",output
        if error:
            print "ret> ",res.returncode
            print "Error> error ",error.strip()
    except OSError as e:
        print "OSError > ",e.errno
        print "OSError > ",e.strerror
        print "OSError > ",e.filename
    except:
        print "Error > ",sys.exc_info()[0]
        logging.info("exception calling systemcommand(" + command +")")
            
def writeconfig():
    with open('/home/pi/scripts/updateopspot/config/configuration.ini', 'w') as configfile:
        config.write(configfile)
        print("configuration.ini was updated")
        

################## THREADS #################

def UploadVideoCloud(n, name):
    global file_name, file_path, CamName
    strnow = strftime("%Y-%m-%d", gmtime())
    print ("rclone will attempt to upload: ")
    print ("- "+ file_name + " to drive folder /" + CamName + "/" + strnow)
    upload_path = "gdrive:" + CamName + "/" + strnow
    command = ["rclone", "copy", file_path, upload_path]
    systemcommand(command)
    print("Success Uploading!")
    

def UploadVideoTelegram(file_name, file_path):
    global shownotificatons, first_record_msg, filesize
    if filesize <= 52428800:
        attempt = 0
        for attempt in range(0, 4):
            attempt += 1 
            try:
                bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.UPLOAD_VIDEO)
                #generate thumb cmd :    ffmpeg -ss 3 -i input.mp4 -vf "select=gt(scene\,0.4)" -frames:v 5 -vsync vfr -vf fps=fps=1/600 out%02d.jpg
                bot.send_video(chat_id=chatid, video=open(file_path, 'rb'), disable_notification=shownotificatons, timeout=160, supports_streaming=True)
                
                failVideo = False
                print("Video: ")
                print("Was successfully sending video on attempt #" + str(attempt))
                attempt = 4
                break
            except:
                print("Failed sending video attempt #" + str(attempt))
                logging.info("Failed sending video attempt #" + str(attempt))
                failVideo = True
    else:
        bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
        fileinfo = "A new video was created but could not be sent as the filesize is" + str(statinfo.st_size) + " Bytes. Max size allowed through telegram is 52428800 Bytes"
        bot.send_message(chat_id=chatid, text=fileinfo)
    if failVideo is True:
        logging.info("Failed sending new mp4 as video trying as document")
        docattempt = 0
        print("Gave up sending as video, trying as document")
        for docattempt in range(0, 1):
            docattempt += 1 
            try:
                bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.UPLOAD_DOCUMENT)
                bot.send_document(chat_id=chatid, document=open(file_path, 'rb'), timeout=180, disable_notification=shownotificatons)
                docattempt = 3
                print("Success (as document)")
            except:
                print("Failed send document attempt #" + str(attempt))
                #logger.info("failed sending as document", user.first_name)
                bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
                bot.send_message(chat_id=chatid, text="a new video was recorded but failed to send after multiple attempts. It is normally a problem with the videos generated being too big in size. You could reduce max record time of clips, quality or resolution. If this keeps occuring contact the developer @ https://t.me/Sealyj or turn off sending of videos with: /dontsend ")
                print("!!! Failed All means of sending video !!! file size?")
                logging.info("Failed All Means of Sending Video - Telegram")
                
def ChooseMethodVideo(bot, file_name, file_path):
    global rcloneupload, sendallvideos, shownotificatons, first_record_msg, filesize
    failVideo = False
    if rcloneupload == True:
        try:
            if file_name != "novideo.mp4":
                outputw = ""
                u = threading.Thread(target = UploadVideoCloud, name = "uploader", args = (0, "uploader"))
                #u.daemon = True
                u.start()
                print("started thread to handle upload")
            else:
                print ("currently no videos to upload")
                logging.info("ChooseMethodVideo called but there are no videos to upload")
        except:
            print ("Exception starting UploadVideoCloud thread @ " + strnow + " in function ChooseMethodVideo()")
            logging.info("Exception starting UploadVideoCloud thread in function ChooseMethodVideo()")
    if file_name is "novideo.mp4" and sendallvideos is True:
        try:
            print("file_name not set sending novideo.mp4")
            bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.UPLOAD_VIDEO)
            bot.send_video(chat_id=chatid, video=open(file_path, 'rb'), disable_notification=shownotificatons, timeout=160, supports_streaming=True)
        except:
            print("failed to send novideo.mp4")
    if file_name is not "novideo.mp4":
        if sendallvideos is True:
            UploadVideoTelegram(file_name, file_path)
        else:
            print("Sendallvideos is False")
            if first_record_msg is True:
                bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
                bot.send_message(chat_id=chatid, text="I detected a new video! 😁")
                bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
                bot.send_message(chat_id=chatid, text="Your settings are configured to not send new videos, if you would like to change this use /sendall 📲")
                bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
                bot.send_message(chat_id=chatid, text="Or ask me to send the latest recorded video with /video 🎬")
                first_record_msg = False
                
def WatchDir(bot, n, name):
    global TOKEN, file_path, file_name, rcloneupload, watched_folder, watchexists, filesize
    logging.info('WatchDir Started')
    while True:
        try:
            print(str(n) + " {} thread started".format(name))
            EXTENSION = "mp4"
            IGNOREEXTENSION = "thumb"
            notifier = inotify.adapters.InotifyTree(watched_folder)
            for event in notifier.event_gen(timeout_s=60):
                #print(event + "in watchdir inotify event gen") 
                if event is not None:
                    if 'IN_CLOSE_WRITE' in event[1] and EXTENSION in event[3] and IGNOREEXTENSION not in event[3]:
                        file_path = event[2] + '/' + event[3]
                        file_name = event[3]
                        print('filter match @ '),
                        print(file_path)
                        statinfo = os.stat(file_path)
                        filesize = statinfo.st_size
                        print("file size is: " + str(filesize))
                        ChooseMethodVideo(bot, file_name, file_path)
        except:
            print("exception watching for new local videos")
            logging.info('exception WatchDir')
            # Relaunch
            WatchDir(bot, 6, "expcreateddirwatch")
def photograb(n, name):
    global photo_path
    global outputp
    global watched_folder
    global image_url
    timespan = 1
    print("#" + str(n) + " getimage thread launched. name: {}".format(name))
    try:
        print ("Searching for jpgs created within the last " + str(timespan) + " minuites in dir " + watched_folder)
        images = [None]
        now = dt.datetime.now()
        ago = now-dt.timedelta(minutes=timespan) #begin selection from x minuites ago to current
        early = now-dt.timedelta(seconds=15) #begin selection x minuites ago to current
        for root, dirs, files in os.walk(watched_folder):
            files.sort()
            for fname in files:
                path = os.path.join(root, fname)
                st = os.stat(path)    
                mtime = dt.datetime.fromtimestamp(st.st_mtime)
                timediff = mtime - early 
                #print (fname)
                if mtime > ago and fname.endswith('.jpg'): # and mtime - timediff < now: # and mtime > daysago
                    images.append(path)
        images.sort(reverse=True)
    except:
        print("Exception in thread #" + str(n) + name + "whilst searching for new local photo")
        
    if images[0] != None:
        print ("critera matched " + images[0])
        temporary = images[0]
        photo_path = temporary
        outputp = "local"
        return
    else:
        try:
            print ("no local files matched criteria - getting a still from stream")
            image_filename = "media/requested_live.jpg"
            img_data = requests.get(image_url).content
            with open(image_filename, 'wb') as handler:
                handler.write(img_data)
            outputp = "stream"
        except: 
            print("Error opening / writing to: " + image_filename)
            print("has network address of camera changed? - returned failure")
            outputp = "failure"
            logging.info('error getting or saving stream image')
            
            
########### BEGIN Message / Command Received Functions ###########
#print('startup')

def start(bot, update):
    global user, chatid, botname
    logging.info('tele req start')
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="Hello and welcome "+user+"!")
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="My name is " + printbotname +".")
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="I provide a secure interface to your 🎥 system")
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="and will only listen to commands sent by you.")
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="You can use the '/' button to choose from a list of commands or type them out yourself")
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="⌨ Type /help for a further explanation ⌨")
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="⌨ Type /settings to see your current configuration")

def maintain(bot, update):
    global user, chatid
    logging.info('tele req maintain')
    text = update.message.text
    testinguser = update.message.from_user
    print ("testinguser = " + str(testinguser))
    update.message.reply_text(
        'Your {}? Yes, I would love to hear about that!'.format(text.lower()))

def ping(bot, update):
    global user, chatid
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="Pong! 🏓")


def report(bot, update):
    global user, chatid
    try:
        logging.info('tele req report')
        print("User requested report")
        bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
        builtreport = subprocess.check_output(["bash", "modules/gethostinfo.sh"])
        bot.send_message(chat_id=chatid, text=builtreport)
    except:
        print("Exception making repot")
        logging.info('exception getting report')
        bot.send_message(chat_id=chatid, text="There was an error whilst processing the report for dispatch. 👎")
        
def sendaudio(bot, update):
    global user, chatid
    global audio_path
    global mp3_path
    import pyaudio, wave, sys
    logging.info('tele req send audio')
    print ("User requested send audio")
    try:
        subprocess.check_output(["rm", "-rf", audio_path])
        subprocess.check_output(["touch", audio_path])
        CHUNK = 8192 #16384 #1024 #8192 #4096
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 48000
        RECORD_SECONDS = 9
        WAVE_OUTPUT_FILENAME = 'media/recording1.wav'
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                input_device_index = 2,
                frames_per_buffer = CHUNK)
        print("* recording")
        bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
        bot.send_message(chat_id=chatid, text="🎤 Recording Audio Clip...")
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
           data = stream.read(CHUNK)
           frames.append(data)
        print("* done recording")
        stream.stop_stream()    # "Stop Audio Recording
        stream.close()          # "Close Audio Recording
        p.terminate()           # "Audio System Close
    
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        #ffmpeg -i input.wav -codec:a libmp3lame -qscale:a 2 output.mp3
        #subprocess.check_output(["ffmpeg", "-i", audio_path, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path])
        bot.send_chat_action(chat_id=id, action=telegram.ChatAction.UPLOAD_AUDIO)
    
        bot.send_audio(chat_id=id, audio=open(audio_path, 'rb'), timeout=30)
        #bot.send_audio(chat_id='580001738', audio=open('tests/test.mp3', 'rb'))
    except:
        print("exception recording audio")
        bot.send_message(chat_id=chatid, text="I had a problem accessing the sound device. Check that the microphone is connected to the top left USB port.")
        logging.info('exception recording audio')
def photo(bot, update):
    global user, chatid
    global photo_path
    global outputp
    global switched2stream
    global switched2local
    logging.info('Tele req photo')
    try:
        outputp = "local"
        p = threading.Thread(target = photograb, name = "photograb", args = (5, "photograb"))
        p.daemon = True
        p.start()
        p.join()
        if outputp == "stream":
            switched2local = False
            if switched2stream == False:
                bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
                bot.send_message(chat_id=chatid, text="I couldn't find any local photos so I'll grab stills from the livestream")
                switched2stream = True
            bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.UPLOAD_PHOTO)
            bot.send_photo(chat_id=chatid, photo=open('media/requested_live.jpg', 'rb'), disable_notification=True)
            os.rename('/home/pi/scripts/opspot/media/requested_live.jpg', '/home/pi/scripts/opspot/media/prev_requested_live.jpg')
        elif outputp == "local":
            switched2stream = False # rearm explanation for switch to stream quality photos
            bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.UPLOAD_PHOTO)
            if photo_path == "nophoto.gif":
                bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
                bot.send_message(chat_id=chatid, text="No image found")
                bot.send_video(chat_id=chatid, photo=open(photo_path, 'rb'), disable_notification=True)
                logging.info('source stream')
            else:
                if switched2local == False:
                    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
                    bot.send_message(chat_id=chatid, text="I'll send high quality local photos from now on")
                    switched2local = True
                bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.UPLOAD_PHOTO)
                bot.send_photo(chat_id=chatid, photo=open(photo_path, 'rb'), disable_notification=True)
                logging.info('source local')
        elif outputp == "failure":
            logging.info('failed to get live or local photo')
            bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
            bot.send_message(chat_id=chatid, text="I couldn't retrieve a local or a live photo, instead I will send your last requested photo.")
            bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.UPLOAD_PHOTO)
            bot.send_photo(chat_id=chatid, photo=open('prev_requested_live.jpg', 'rb'), disable_notification=True)
        else:
            print('outputp unknown value = '),
            print(outputp)
    except:
        print ("failed all send requested_live.jpg") 
        bot.send_message(chat_id=chatid, text="Sorry I couldn't get any photos at all :S")
        logging.info('Exception sending photo')
        
def video(bot, update):
    global user, chatid, file_name, file_path, filesize
    logging.info('Tele req latest video')
    UploadVideoTelegram(file_name, file_path)


def sendall(bot, update):
    global user, chatid
    global sendallvideos
    logging.info('Tele req sendall true')
    config['TELEGRAM']['SendAll'] = "True"
    writeconfig()
    sendallvideos = True
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="Newly generated videos will be sent to you 📸 ")


def dontsend(bot, update):
    global user, chatid
    global sendallvideos
    logging.info('Tele req sendall false')
    config['TELEGRAM']['SendAll'] = "False"
    writeconfig()
    sendallvideos = False
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="Newly generated videos won't be sent to you 📷")


def motionon(bot, update):
    global user, chatid
    logging.info('Tele req motion / vid rec off')
    config['CAMERA']['Motion'] = "True"
    writeconfig()
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="Motion detection started, movement will be saved to host storage. 🎥 🏃‍")
    subprocess.check_output(["wget", "-O-", "http://127.0.0.1:7999/1/detection/start", ">/dev/null"])


def motionoff(bot, update):
    global user, chatid
    logging.info('Tele req motion / vid rec off')
    config['CAMERA']['Motion'] = "False"
    writeconfig()
    pause = 'http://127.0.0.1:7999/1/detection/pause'
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="Motion detection will be paused, recording will cease until restarted. 🎥 ⏸ ")
    subprocess.Popen(["wget", "-O-", pause, ">", "/dev/null"])


def notificationson(bot, update):
    global chatid
    global user
    global shownotificatons
    logging.info('Tele req notify on')
    config['TELEGRAM']['Notifications'] = "True"
    writeconfig()
    shownotificatons = True
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="You will see and hear notifications when a video or photo arrives. 🔊 ")


def notificationsoff(bot, update):
    global user, chatid
    global shownotificatons
    logging.info('Tele req notify off')
    config['TELEGRAM']['Notifications'] = "False"
    writeconfig()
    shownotificatons = False
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="You will not see / hear notifications when a video or photo arrives. 🔇 ")

def showsettings(bot, update):
    global user, chatid
    logging.info('Tele req showsettings')
    rec=str(motionbool)
    upl=str(rcloneupload)
    sen=str(sendallvideos)
    noti=str(shownotificatons)

    currentsettings = "Your Current Settings: \n------------------------------\nRecording:{0}\nUploads:{1}\nSending:{2}\nNotifications:{3}".format(rec, upl, sen, noti)
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text=currentsettings)
    

def commandslist(bot, update):
    global user, chatid
    logging.info('Tele req commandslist')
    #formatting looks insane but actually works in telegram output
    hiddencommands = """
 Hidden commands:
------------------------------
 /help                 - Comprehensive help guide
 /update               - Check for updates to OpSpot
 /shutdown             - Power off system
 /restart                   - Restart the system
 /uploadson            - Enable upload to cloud
 /uploadsoff           - Disable upload to cloud
 /motionon             - Enable record videos
 /motionoff            - Disable record videos
 /report                   - Show System info
 /settings             - Show current user settings
 /ping                      - Confirm connection
 /share                 - Suggest to friends and family
                """
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text=hiddencommands)
    
    

def share(bot, update):
    global user, chatid, releaseversion
    logging.info('Tele req share info')
    contactinfo = r"""\..
                          
                 (`/\
                 `=\/\
                  `=\/\
                   `=\/
                        \
                   OpSpot
         IOT Bot Security System 
                  by J. Slade
                     ver:{}
               Support/Contact:
---------------------------------------------------
            sealedjoy@gmail.com
             telegram: @Sealyj
           
                """.format(releaseversion)
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text=contactinfo)

def helpcommand(bot, update): 
    global user, chatid
    logging.info('Tele req help')
    #~ helpstrings = []
    #~ helpstrings.append(helpstring0) # etc etc
    #~ helpstring = 0
    #~ for helpstring, line in enumerate(helpstrings):
        #~ bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
        #~ bot.send_message(chat_id=chatid, text=helpstrings[helpstring])
    helppath = "help.txt"
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.UPLOAD_DOCUMENT)
    bot.send_document(chat_id=chatid, document=open(helppath, 'rb'), timeout=180, disable_notification=shownotificatons)

def stop_and_restart():
    """Gracefully stop the Updater and replace the current process with a new one"""
    print("User requested restart of script!")
    updater.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)

def uploadson(bot, update):
    global user, chatid, rcloneupload
    logging.info('Tele req upload true')
    print("User enabled uploads")
    config['CLOUD']['Upload'] = "True"
    writeconfig()
    rcloneupload = True
    bot.send_message(chat_id=chatid, text='I will attempt upload of all recorded videos to your Google Drive account ⛅')

def uploadsoff(bot, update):
    global user, chatid, rcloneupload
    logging.info('Tele req uploads false')
    print("User disabled uploads")
    config['CLOUD']['Upload'] = "False"
    writeconfig()
    rcloneupload = True
    bot.send_message(chat_id=chatid, text="I won't upload anything to your Google Drive account ⛅")

def restart(bot, update):
    global user, chatid
    logging.info('Tele req reboot')
    print("User requested a restart")
    bot.send_message(chat_id=chatid, text='💤 System will restart...')
    restartcommand = ["sudo", "shutdown", "-r", "now"]
    systemcommand(restartcommand)
    #Thread(target=stop_and_restart).start()


def shutdown(bot, update):
    global user, chatid
    logging.info('Tele req shutdown')
    print("User requested shutdown")
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="Camera will shutdown and be safe to move after 90 seconds, to turn camera back on simply reconnect the power‍ supply to the system")
    shutdowncommand = ["sudo", "shutdown", "-h", "now"]
    systemcommand(shutdowncommand)

def checkforupdate(bot, update):
    global user, chatid, scriptpath, downloadscriptpath, downloadscriptfolder, updateflaglocation
    print("UPDATE: User requested update")
    logging.info('User requested update check')
    canupdate = "none"
    try:
        bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
        bot.send_message(chat_id=chatid, text="Checking for update, one moment...")
        updatecommand = ["rclone", "copy", "-v", "gdrive:packages/update/opspot/python-telegram-bot.py", downloadscriptfolder]
        subprocess.check_output(updatecommand)
    except:
        print("Exception downloading python-telegram-bot for update check")
    try:
        checkcommand = ["cmp", "--silent", scriptpath, downloadscriptpath]  #"cmp", "--silent", scriptpath, downloadscriptpath
        subprocess.check_output(checkcommand)
        print("File was the same - no need to update")
        canupdate = "none"
    except:
        
        print ("File is different - can update")
        canupdate = "new"
        with open(updateflaglocation, "w") as text_file:
            text_file.write("{0}".format(canupdate))
    if canupdate is "new":
        print("New file found send prompt to user to do a /restart command when possible" )
        bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
        bot.send_message(chat_id=chatid, text="New software is availible! "  + emoji.emojize(':beaming_face_with_smiling_eyes:'))
        bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
        bot.send_message(chat_id=chatid, text="Send me a /restart command when you are ready to apply the update")
        bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
        bot.send_message(chat_id=chatid, text="The updating process typically around four minutes, during which all functions will be temporarily unavailible")
        logging.info('Update found - changed flag for reboot - User offered prompt to reboot to begin update')
    else:
        print("Already on the latest version")
        bot.send_message(chat_id=chatid, text="I am already running the latest version")
        logging.info('No update found')

def echo(bot, update):
    global user, chatid
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text=update.message.text)


def unknown(bot, update):
    global user, chatid
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text="Sorry, I didn't understand that command " + emoji.emojize(':downcast_face_with_sweat:'))



def error_callback(bot, update, error):
    try:
        logging.info('Callback error - telegram')
        raise error
    except Unauthorized:
        print("Error:Unauthorized")
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("Error:BadRequest")
        # handle malformed requests - read more below!
    except TimedOut:
        print("Error:TimedOut")
        # handle slow connection problems
    except NetworkError:
        print("Error:NetworkError")
        # handle other connection problems
    except ChatMigrated as e:
        print("Error:ChatMigrated")
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print("Error:TelegramError")
        # handle all other telegram related errors


############ END Message / Command Received Functions ############

                
def main():
    global scriptupdatedflag, TOKEN, file_path, rcloneupload, botname, username
    updater = Updater(token=TOKEN, request_kwargs={'read_timeout': 600, 'connect_timeout': 600})
    # Create the Updater and pass it your bot's token.
    dispatcher = updater.dispatcher
    # Get the dispatcher to register handler

# Start command handlers 
    start_handler = CommandHandler('start', start, filters=Filters.user(username=user))
    dispatcher.add_handler(start_handler)
    
    sendaudio_handler = CommandHandler('audio', sendaudio, filters=Filters.user(username=user))
    dispatcher.add_handler(sendaudio_handler)
    
    photo_handler = CommandHandler('photo', photo, filters=Filters.user(username=user))
    dispatcher.add_handler(photo_handler)
    
    video_handler = CommandHandler('video', video, filters=Filters.user(username=user))
    dispatcher.add_handler(video_handler)
    
    sendall_handler = CommandHandler('sendall', sendall, filters=Filters.user(username=user))
    dispatcher.add_handler(sendall_handler)
    
    dontsend_handler = CommandHandler('dontsend', dontsend, filters=Filters.user(username=user))
    dispatcher.add_handler(dontsend_handler)
    
    notificationson_handler = CommandHandler('notificationson', notificationson, filters=Filters.user(username=user))
    dispatcher.add_handler(notificationson_handler)
    
    notificationsoff_handler = CommandHandler('notificationsoff', notificationsoff, filters=Filters.user(username=user))
    dispatcher.add_handler(notificationsoff_handler)

    helpcommand_handler = CommandHandler('help', helpcommand, filters=Filters.user(username=user))
    dispatcher.add_handler(helpcommand_handler)
    
    # Show a list of commands
    commandslist_handler = CommandHandler('commands', commandslist, filters=Filters.user(username=user))
    dispatcher.add_handler(commandslist_handler)
    
    # Hidden commands 
    share_handler = CommandHandler('share', share, filters=Filters.user(username=user))
    dispatcher.add_handler(share_handler)
    
    uploadson_handler = CommandHandler('uploadson', uploadson, filters=Filters.user(username=user))
    dispatcher.add_handler(uploadson_handler)
    
    uploadsoff_handler = CommandHandler('uploadsoff', uploadsoff, filters=Filters.user(username=user))
    dispatcher.add_handler(uploadsoff_handler)
    
    motionon_handler = CommandHandler('motionon', motionon, filters=Filters.user(username=user))
    dispatcher.add_handler(motionon_handler)
    
    motionoff_handler = CommandHandler('motionoff', motionoff, filters=Filters.user(username=user))
    dispatcher.add_handler(motionoff_handler)
    
    ping_handler = CommandHandler('ping', ping, filters=Filters.user(username=user))
    dispatcher.add_handler(ping_handler)
    
    report_handler = CommandHandler('report', report, filters=Filters.user(username=user))
    dispatcher.add_handler(report_handler)
    
    restart_handler = CommandHandler('restart', restart, filters=Filters.user(username=user))
    dispatcher.add_handler(restart_handler)
    
    shutdown_handler = CommandHandler('shutdown', shutdown, filters=Filters.user(username=user))
    dispatcher.add_handler(shutdown_handler)
    
    checkforupdate_handler = CommandHandler('update', checkforupdate, filters=Filters.user(username=user))
    dispatcher.add_handler(checkforupdate_handler)
    
    showsettings_handler = CommandHandler('settings', showsettings, filters=Filters.user(username=user))
    dispatcher.add_handler(showsettings_handler)
    
    maintain_handler = CommandHandler('maintain', maintain, filters=Filters.user(username="Sealyj"))
    dispatcher.add_handler(maintain_handler)
    

    # echo user input
    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)
    # reply if command is unknown
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)
    
    dispatcher.add_error_handler(error_callback)
    
    # log all errors
    ########### END HANDLERS ##########

                    
    # Start the Bot
    updater.start_polling()
    logging.info('Polling started')
    #emoji = "💤👋🤙🙌✌"
    #greetingemoj = [1,2,3,4,5]
    #wave = random.choice(greetingemoj)
#    startupmsg1 = "Beep boop. Hello "+ user + "! " + emoji.emojize(':alien_monster:')
    startupmsg2 = printbotname + " reporting in! " + emoji.emojize(':alien_monster:')
    startupmsg3 = emoji.emojize(':detective:') + " I'm back up and listening. "
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text=startupmsg2)
    bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
    bot.send_message(chat_id=chatid, text=startupmsg3)
    print("Bot started: Waiting for commands")
    if bot != None:
        outputw = ""
        w = threading.Thread(target = WatchDir, name = "mp4cam", args = (bot, 5, "mp4watch"))
        w.daemon = True
        w.start()
        startwatch = False
        logging.info('Started Inotify MP4 Watch')
    else:
        print ("waiting for /start command")
        bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
        bot.send_message(chat_id=chatid, text="Waiting for user command: ")
        bot.send_message(chat_id=chatid, text="/start")
        logging.info('Bot could not be contacted')
    if scriptupdatedflag is True:
        print ("New version of script detected")
        if scriptdowngraded is False:
            print ("Script was upgraded")
            bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
            bot.send_message(chat_id=chatid, text="I have been updated! 😇")
            scriptupdatedflag = False
            logging.info('Script was updated')
        elif scriptdowngraded is True:
            print("Script was downgraded")
            bot.send_chat_action(chat_id=chatid, action=telegram.ChatAction.TYPING)
            bot.send_message(chat_id=chatid, text="I have downgraded to a preferred version! 😇")
            logging.info('Script was downgraded')
        
    #w.join()
    
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    print("after updater.idle() - main() finished")
    print("python-telegram-bot.py will exit now")
    logging.info('Finished - now exiting')


if __name__ == '__main__':
    print("Running as main module Loading...")
    writeconfig()
    logging.info('Wrote initial settings to config now starting main()')
    main()
else:
    print("Error: This script should be ran as __main__")
    logging.info('Script is not being called as __main__')
        

