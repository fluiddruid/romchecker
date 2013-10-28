#!/usr/bin/env python

# ROMChecker
# by Andrew Robinson
#
# A simple script to check for the existence of the new nightly build of a ROM
# and send a Pushover notification (http://pushover.net/) to an Android device 
# if it finds one.
#
# I wrote this to check for the nightly builds of the excellent PAC-ROM 
# (http://http://pac-rom.com), but it will work for other ROM. which have 
# date stamped nigtlies on a publicly accessible web server.
# 
# I schedule this to run every half hour using cron. Please don't poll other 
# people's servers too frequently!

# Import the date, HTTP and URL libraries.
import datetime, httplib, urllib, urllib2

# Get today's date, so we can use it in the ROM filename.
date = datetime.date.today()

# User configuration goes here.
# ROM name and file name.
rom_name = "PAC-ROM"
rom_file_name = "pac_n7100-nightly-" + date.strftime('%Y%m%d') + ".zip"

# ROM file location on the web. 
rom_file_url = "http://pacman.basketbuild.com/download.php" +
               "?file=main/n7100/nightly/" + 
			   rom_file_name

# Log file location on the local computer. Make sure that this is writable by
# the user running the script.
log_file_name = "/var/log/pacromchecker.log"

# Pushover API token and user key.
pushover_token = ""
pushover_user = ""

# There should not be any need for an end user to have to edit anything below
# here.

# We use a counter to keep track of how many errors we've hit.
errors = 0

# Use a try/except to catch and print details of any errors, and a finally to
# act on the result.
try:
  # Check the server for the ROM using urlopen. This will give an error if it
  # doesn't exist.
  print "Checking the web server for " + rom_file_name + "."
  urllib2.urlopen(rom_file_url)

except urllib2.URLError, e:
   # We got some sort of error.
   print "Could not find " + rom_file_name + ". The error given was:\n" + str(e)
   errors+=1

finally:
  # Only attempt to do anything if we've not hit any errors.
  if errors == 0:

    print rom_file_name + " exists on the server!"

    # Check to see if we've already sent a notification today. We keep a list 
    # of processed ROMs, so we can just look in there.
    log_file = open(log_file_name, 'r')
    log_list = log_file.readlines()
    log_file.close()

    # Look for today's ROM in the log file.
    found = False
    
    for line in log_list:
      if rom_file_name in line:
        found = True
		print "Already sent a notification about " + rom_file_name + "."

    # Only continue if the ROM hasn't been logged.
    if not found:
      
      # Log the ROM.
      log_file = open(log_file_name, 'a')
      log_file.write(rom_file_name + "\n")
      log_file.close()

      # Send the notification.
      print "Sending notification about " + rom_file_name + "."
     
      conn = httplib.HTTPSConnection("api.pushover.net:443")
      conn.request("POST", "/1/messages.json",
      urllib.urlencode({
        "token": pushover_token,
        "user": pushover_user,
        "message": "Today's build of " + rom_name + " is now available.",
        "title":  rom_name + " available!",
        "url_title": "Download",
        "url": rom_file_url,
        }), { "Content-type": "application/x-www-form-urlencoded" })
      conn.getresponse()

