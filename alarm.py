#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2009-2012 Canonical Ltd.
#
# Authors: Neil Jagdish Patel <neil.patel@canonical.com>
#          Jono Bacon <jono@ubuntu.com>
#          David Planella <david.planella@ubuntu.com>
#          Janitha Karunaratne <janitha@janitha.com> (for alarm code)
#          Jeremy B. Merrill <jeremy@jeremybmerrill.com> (for combining alarm code and this applet)
# 
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of any or all of the following licenses:
#
# 1) the GNU Lesser General Public License version 3, as published by the
# Free Software Foundation; and/or
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the applicable version of the GNU Lesser General Public
# License for more details; and/or
#
# 3) (MIT License) 
#    Permission is hereby granted, free of charge, to any person obtaining a 
#    copy of this software and associated documentation files (the "Software"),
#    to deal in the Software without restriction, including without limitation 
#    the rights to use, copy, modify, merge, publish, distribute, sublicense, 
#    and/or sell copies of the Software, and to permit persons to whom the 
#    Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
#    DEALINGS IN THE SOFTWARE.
#
# You should have received a copy of both the GNU Lesser General Public
# License version 3 and version 2.1 along with this program.  If not, see
# <http://www.gnu.org/licenses/>
#

import os
import platform
import sys

import gtk

import pygtk
pygtk.require("2.0")
import time #NEW
import subprocess #NEW


import pynotify

import gobject
import appindicator


def _(s): #TODO: implement. :)
  return s

sysfs_dir = "/sys/block"

def compare_linux_version(wanted_version):
    version = map(int, platform.release().split("-")[0].split("."))
    major_version_greater = version[0] > wanted_version[0] 
    minor_version_greater = version[0] >= wanted_version[0] and version[1] > wanted_version[1]
    bugfix_version_greater = version[0] >= wanted_version[0] and version[1] >= wanted_version[1] and version[2] >= wanted_version[2]
    return major_version_greater or minor_version_greater or bugfix_version_greater

version_at_least_2_6_27 = compare_linux_version([2, 6, 27])

THRESHOLD_ALERT = 10
THRESHOLD_ALARM = 40

SOUND_ARMED = "mpg321 ./bleep.mp3 -q"
SOUND_ALERT = "mpg321 ./alert.mp3 -q"
SOUND_ALARM = "mpg321 ./alarm.mp3 -q -g "


POLLING_FREQUENCY = 500 #milliseconds

class ThinkHDAPSApplet:
    """Applet that shows the status of HDAPS.

       This class partly copyright (C) 2008 - 2010  onox <denkpadje@gmail.com>, from AWN-extras
    """

    __error_occurred = False
    __n = None
    __show_notifications = False

    def __init__(self):
        if version_at_least_2_6_27:
            #from Janitha
            #contents are just "(123,456)" for x,y position.
            self._hdaps_position = "/sys/devices/platform/hdaps/position"
        else:
            #I have no idea if this works.
            self._hdaps_position = "/sys/devices/platform/hdaps/position"

        self.ind = appindicator.Indicator("hdaps-theft-alarm-indicator",
                                           "purse-thief",
                                           appindicator.CATEGORY_HARDWARE)
        self.ind.set_status(appindicator.STATUS_ACTIVE)
        self.ind.set_icon("purse-thief")

        #TODO: persist this.
        self.__quiet_mode = False

        self.menu_setup()
        self.ind.set_menu(self.menu)
        #######

        self.ind.set_status(appindicator.STATUS_ACTIVE)

    def _notify_armed(self):
        for i in range(0, 1): #was 3
          os.system(SOUND_ARMED)
          time.sleep(1)
        os.system(SOUND_ALERT)

    # def _change_icon_status(self, armed):
    #     if armed:
    #         #change icon to armed status
    #     else:
    #         #change icon to unarmed status

    def _within_alarm_threshold(self):
        x, y = self._get_position()
        x_okay = x > self.initial_x - THRESHOLD_ALARM and x < self.initial_x + THRESHOLD_ALARM
        y_okay = y > self.initial_y - THRESHOLD_ALARM and y < self.initial_y + THRESHOLD_ALARM
        return x_okay and y_okay

    def _within_alert_threshold(self):
        x, y = self._get_position()
        x_okay = x > self.initial_x - THRESHOLD_ALERT and x < self.initial_x + THRESHOLD_ALERT
        y_okay = y > self.initial_y - THRESHOLD_ALERT and y < self.initial_y + THRESHOLD_ALERT
        return x_okay and y_okay

    def _sound_the_alert(self, x, y):
        #beep!
        diff = abs(self.initial_x-x) + abs(self.initial_y-y)
        gain_diff = int((diff*100.0) / (THRESHOLD_ALERT))*2
        print "alert",gain_diff
        cmd = SOUND_ALERT + " -g " + `gain_diff`
        print cmd
        os.system(cmd)

    def _sound_the_alarm(self):
        if self.__quiet_mode:
            gain_amt = 10
        else:
            gain_amt = 1000 
        os.system(SOUND_ALARM + str(gain_amt))

    def _computer_unlocked(self):
        os.popen('gnome-screensaver-command -q').readlines()[0].find("inactive") > 0

    def arm(self, throwaway_widget_argument):
        self.initial_x, self.initial_y = self._get_position()
        print self.initial_x
        print self.initial_y
        x = self.initial_x
        y = self.initial_y

        #go into screensaver mode
        os.system("gnome-screensaver-command -l")

        self._notify_armed()
        #self._change_icon_status(True)


        while self._within_alarm_threshold():
            time.sleep(0.05)

            # Read HDAPS values
            if not self._within_alert_threshold():
                x, y = self._get_position()
                self._sound_the_alert(x, y)

            #if the user has unlcoked the computer, thus disarming the alarm.
            if self._computer_unlocked():
                print "Unlocked -> disarmed"
                return #disarm, but don't quit the program

        # if we've reached this point, the laptop has exceeded the threshold while armed
        # time to start the alarm!
        while 1:
            #stop the alarm when the correct password is entered.
            if self._computer_unlocked():
                print "Unlocked -> disarmed (after alarm activated)"
                return  #disarm, but don't quit the program

            print "Alarm!"
            self._sound_the_alarm()
            time.sleep(1.4)

    def _get_position(self):
        # Read HDAPS values
        try:
            file = open(self._hdaps_position)
        except IOError:
            raise IOError, "Couldn't find the HDAPS position file."
        value = file.readline()
        x = int(value.partition("(")[2].partition(",")[0])
        y = int(value.partition(",")[2].partition(")")[0])
        file.close()
        return x,y

    #intentional design decision:
    #only one icon, because the screensaver is on when the thing is armed.

    def toggleQuietMode(self, widget):
        if widget.active:
            self.__quiet_mode = True
        else:
            self.__quiet_mode = False

    def menu_setup(self):
        self.menu = gtk.Menu()
        self.arm_item = gtk.MenuItem("Arm")
        self.arm_item.connect("activate", self.arm) 
        self.arm_item.show()
        self.menu.append(self.arm_item)
        self.seperator_item = gtk.SeparatorMenuItem()
        self.menu.append(self.seperator_item)
        self.test_mode_item = gtk.CheckMenuItem("Test Mode (Quieter)")
        self.test_mode_item.set_active(False)
        self.test_mode_item.connect("activate", self.toggleQuietMode)
        self.test_mode_item.show()
        self.menu.append(self.test_mode_item)
        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit) 
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def quit(self, widget):
        sys.exit(0)

    def main(self):
        #sitting on the dock of the viewport, until armed.
        gtk.main()

if __name__ == "__main__":
  indicator = ThinkHDAPSApplet()
  indicator.main()

