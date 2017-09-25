#!/usr/bin/python

import sys
import RPi.GPIO as GPIO
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# Address/Groups to send to
carrie_text='@vtext.com'
randy_text='@messaging.sprintpcs.com'
carrie_email='@cox.net'
randy_email='@cox.net'
dummy_email='@cox.net'
exception=0

send_to_alarm=[randy_email,randy_text,carrie_text,carrie_email]
# send_to_arm=[randy_email,carrie_email]
send_to_arm=[randy_email]
# send_to_arm=[dummy_email]

# This creates an email and sends it to an address of your choosing directly from python
def mailsend (recipients,sender,subject):
  try:
    print "Sending alert messages to: ",recipients,"Subject:",subject,
    s=smtplib.SMTP('smtp.cox.net')
    # s.set_debuglevel(1)
    
    # If the previous mail caused an exception, let the recipient know
    global exception
    if exception == 1:
      subject += 'A previous message caused an exception and was unable to send an e-mail.'

    msg = MIMEText(subject)
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = "Home Alarm Alert Message" 
    s.sendmail(sender, recipients, msg.as_string())
    s.quit()
    s.close()
    exception=0
  except Exception as e: 
    print "Caught exception in the e-mail function: %s" % (e) 
    exception=1
########################################################################################

GPIO.setmode(GPIO.BOARD)
 
# Set up the GPIO channels
GPIO.setmode(GPIO.BOARD)
GPIO.setup(29, GPIO.IN)
GPIO.setup(33, GPIO.IN)
 
# Read the current sensor state as our starting point
# The sensors read reversed logic so:
#   0 = Armed and Alarming
#   1 = Disarmed and Quiet
armstate = GPIO.input(29)
alarmstate = 1 # Assume not in alarm, and report if it is in alarm
armtimer=0

while True:

    # Input from the sensors
    armsensor = GPIO.input(29)
    alarmsensor = GPIO.input(33)

    # Display the GPIO state
    # print armsensor, alarmsensor
    tm = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sys.stdout.write(tm)
    if armsensor == 0:
        sys.stdout.write ("  -  Alarm is Armed [0]  &  ")
    else:
        sys.stdout.write ("  -  Alarm is Disarmed [1]  &  ")

    if alarmsensor == 0:
        sys.stdout.write ("Alarm is Alarming [0]\n")
    else:
        sys.stdout.write ("Alarm is Clear [1]\n")


    #####################################################################################
    # This is the Alarm sensor check
    if alarmsensor != alarmstate:
        # The alarm state has changed
        alarmstate = alarmsensor
        if alarmstate == 0:
            print "The home alarm is alarming! (0)"
            mailsend (send_to_alarm,'randyscott@cox.net','The Home Alarm Is Alarming at: ' + tm + '\n')
        else:
            print "The home alarm has cleared. (1)"
            mailsend (send_to_alarm,'randyscott@cox.net','The Home Alarm Has Cleared at: ' + tm + '\n')
    #####################################################################################

    # As long as we're in an alarm state, we ignore the Arm sensor which is flashing and unreliable.  Go back to the top of the loop until alarm clears.
    if alarmstate == 0:
        print "Ignoring the ARM sensor while in alarm."
        sys.stdout.flush()
        time.sleep(5)
        continue

    #####################################################################################
    # This is the ARM sensor check
    if armsensor != armstate:
        # We need the sensor to be different than state for >40 seconds before we flip the flag 
        if armtimer > 40:
            # Here means that the flag and sensor have been different for > 40 seconds
            armstate = armsensor
            if armstate == 0:
                print "The home alarm is armed. (0)"
                mailsend (send_to_arm,'randyscott@cox.net','The Home Alarm Is Armed at: ' + tm + '\n')
            else:
                print "The home alarm is disarmed (1)"
                mailsend (send_to_arm,'randyscott@cox.net','The Home Alarm Is Disarmed at: ' + tm + '\n')
        else:
            # Here means that the flag and sensor have been different for less than 40 seconds.  Keep waiting.
            armtimer = armtimer + 5
            if armtimer == 5:
                print "The ARM sensor has changed.  Waiting 45 seconds for it to stabilize."

    else:
        # Here means that the flag and sensor are the same.  Reset the timer and keep going
        armtimer=0
    #####################################################################################

    sys.stdout.flush()
    time.sleep(5)
 

