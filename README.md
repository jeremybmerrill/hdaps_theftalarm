#HDAPS Theft Alarm for Ubuntu Unity
=================================
A theft alarm for laptops with a Hard Drive Active Protection System and Ubuntu's Unity shell.

Jeremy B. Merrill
jeremy@jeremybmerrill.com
Copyright 2013 // GPL v3 or MIT

This is a simple theft alarm for laptops with HDAPS, controlled by a Unity indicator. HDAPS (Hard Drive Active Protection System) is, I think, only present on some Apple and Lenovo laptops. I use the tp_smapi module on my Lenovo laptop, but YMMV.

####Install
Mve the icon into /usr/share/icons/hicolor/scalable/devices and then regenerate the GTK icon cache (or else the icon won't show up). See INSTALL for more info.

####Usage
1. $ python alarm.py #or set the script to run on startup.
2. Click the Arm option on the indicator to drop the computer into screensaver mode and arm the alarm.
3. Unlock the computer with your password to disarm the alarm.
4. If, before the alarm is disarmed, the laptop is moved, it will (loudly) alarm. If it's moved only a little bit, it will beep as a warning. The volume of the warning beep varies in direct proportion with the magnitude of the move.

####License
This software is available under a GPL v3 license, see the included LICENSE file. The icons are licensed under CC BY 3.0; the [Purse Thief](http://thenounproject.com/noun/purse-thief/#icon-No3496) icon was designed by [Katie M Westbroook](http://thenounproject.com/katiemwestbrook) from [The Noun Project](http://thenounproject.com Noun Project) and modified by Jeremy B. Merrill.

#### Credits
This software is based almost entirely off of Janitha Karunaratne's [jtheftalarm](http://stuff.janitha.com/jblog/jtheftalarm.txt) script and [Ubuntu's sample Python Unity indicator](http://developer.ubuntu.com/resources/technologies/application-indicators/ Unity).

Pull requests and/or questions are welcome. :)




