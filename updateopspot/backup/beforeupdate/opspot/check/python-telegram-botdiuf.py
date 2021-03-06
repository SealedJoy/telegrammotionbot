29/01/2019 OpSpot ver 0.1
----------------------------

How do I update the software? 

- As bugfixes, security updates and new features are created they will be stored on an update server
- To check for updates to the current program use /checkforupdate
 
   
I am having a problem with the camera? / I don't understand something?

- Most problems are to do with the network or storage and are trivial to fix, if you are unsure about anything or the camera is not working in the way it is meant to be, contact the developer!
  
  
Is there an easy way to save a particular video?

- You can forward messages recived in telegram to your saved messages, this is a seperate chat and will hold files there even when deleted from camera, cloud and bot chat.
- You can download and save media locally to be used with other apps and programs try long pressing on the media file and select share.
    

Where are my videos and photos stored?

- Videos are recorded to the cameras local sd card and or attached harddrive, depending on the configured storage media they will be automatically deleted when older than 1 - 7 days
- If uploading videos to cloud is enabled each video will be copied to your cameras google drive account
- If sending all videos via telegram is enabled or your requested a certain video then you will have copies of your videos on that telegram account.

    
Can I view my camera on a different device?

- You can access your camera and media in 2 ways:

- Externally (when not on your network)
    Telegram can be installed across a multitude of devices, search for it on your devices app store or within a web-browser.

- Internally (When on a device connected to the network:
    In telegram send a /report command to your camera, click on or type the interface address into a webbrowser and bookmark it for easy viewing!

    The camera system's media storage is also configured as a network drive and can be accessed from other devices on the network:
      On Mac OSX, open Finder, in the top bar select 'Go' then 'Network'
      On Windows, open File Explorer, Select 'Network'
      or on any device type smb:// followed by your hostname and .local
      example: smb://frontcamera.local
-Tips:
   You can get a link to the local camera interface from /report command in telegram.
   I would not suggest changing settings in the camera interface.
- Ask the developer about automatically displaying the camera stream on a TV when motion is detected / dedcating a screen or device for monitoring.


Can I view my camera live externally?

- It can be done relatively safely but I would highly advise against it (due to security implications)
- I would suggest you instead use the automatic send video function. Which will deliver each recorded video to you as they are generated. Depending on the the settings of your system, internet speed etc, you can start viewing the motion event within 10 - 20 seconds of video creation. So your realtime lag can be as low as 30 seconds.

Camera keeps sending videos with nothing happening in?

- This is probably because something else is triggering the motion detection, perhaps a window, pictureframe or mirror.
- You could either mask of the problematic area that is false triggering the detection or decrease the motion detection sensitivity
  To change these settings:
    Login as admin to camera, select settings (top left button) and scroll down to motion detection, click on it to expand the menu.
    - Mask off an area from motion detection:
        Turn mask on, select mask type as editable, click edit mask, now colour the area of picture in dark you wish the cameras motion detection to ignore, Hit save mask, hit apply. Done!
    - Decrease motion detection sensitivity:
        Increase the frame change threshold slider by 1%, hit apply, test settings, increase if needed.
- If you are unsure about this don't hesitate to contact the developer
    

Why am I getting low quality photos?

- If your camera is configured to take photos as well as video, it will prefer these higher quality images and send the images when you request an image with the command: /photo but if its not setup to take photos it will return a grab from the livestream, this image will likely be much more up to date but of a lower resolution.
   

Is this safe, can anyone else see my camera?

- Many cheap camera manufactures use proprietry apps to manage their IOT camera systems, such apps are often created quickly and without proper security precautions. Often containing data collection programs and malware themselves. The physical hardware is often found to contain hardcoded 'backdoors'
- Even established brands have had recent media scandles involving access to their customers cloud stored data.
- Your files are encrypted before being sent and only you have access to your telegram bot and the media it has sent to you.
- Telegram is perhaps 'THE' most secure and trusted methods of communication availble today. It's dependable, quick and easy to use. All of it's code is transparent and viewable and audited by independant bodies (unlike others)
- Your camera is protected from unwanted snooping by password protected access on your local network, even others on your network cannot access the system.
   
Do I need cloud storage?

- Telegram provides essentially unlimited storage of files sent in chat so if you are using /sendall and don't wish to use continous recording or wish to keep locally then just use telegram.
- If you want higher quality/resolution or longer videos these will be of a greater size and likely not accepted by telegram, if you wanted remote access to these videos then you could use a cloud account for uploading these files.
     

Do I need to do anything to maintain the camera system / telegram bot?

- We recommend you clear your chat with the bot every week to once a month depending on the volume of incoming videos and your devices processing power 
- You may also wish to clear the telegram app data/cache around the same time if you are low on device space.
- We also recommend sending a reboot command once a month to keep things responsive - however this is not essential.
     

How do I contact the developer?

     - The developer will be happy to help you with any problems you may have regarding telegram, camera systems, security etc
     - Contact Joseph Slade:
       Email: sealedjoy@gmail.com
       Telegram: @Sealyj
       Phone: 07983629226