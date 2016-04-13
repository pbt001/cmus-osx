#!/usr/bin/python
import sys
import os
import json

try:
    from Foundation import NSUserNotification
    from Foundation import NSUserNotificationCenter
    import AppKit
except ImportError as e:
    print('error: you need pyobjc package to use this feature.\n')
    raise e


CMUS_OSX_CONFIG = os.path.expanduser('~/.config/cmus/cmus-osx.json')
UPDATE_OPTIONS_FROM_CONFIG = True

# default options may be over-written from cmus-osx.json file
#  if UPDATE_OPTIONS_FROM_CONFIG is true

# DISPLAY_MODE controls the notification verbosity
#  0 shows nothing, immediately quits
#  1 replace old notification with new one in notification center
#  2 clears old notifications, add new one
#  3 shows a new notification for each cmus status change
DISPLAY_MODE = 2

# the icon file path for notification, or set as '' to disable icon displaying
ICON_PATH    = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/Actions.icns'


#------------------------------------------------------------------------------
class CmusArguments:
    def __init__(self, argv):
        self.title    = ''
        self.subtitle = ''
        self.message  = ''
        self.tags     = {
                'status': '',
                'artist': '',
                'album': '',
                'track': '',
                'title': '',
                'date': ''
                }

        argc = len(argv)
        if argc < 4:
            print('invalid arguments')
            sys.exit(1)

        n = 1
        while n < argc:
            arg = argv[n]

            if arg == 'status':
                n += 1
                self.tags['status'] = argv[n]
            elif arg == 'artist':
                n += 1
                self.tags['artist'] = argv[n]
            elif arg == 'album':
                n += 1
                self.tags['album'] = argv[n]
            elif arg == 'tracknumber':
                n += 1
                if argv[n] and argv[n] != '0':
                    self.tags['track'] = argv[n]
            elif arg == 'title':
                n += 1
                self.tags['title'] = argv[n]
            elif arg == 'date':
                n += 1
                if argv[n] and argv[n] != '0':
                    self.tags['date'] = argv[n]

            n += 1


    def make(self):
        if self.tags['status']:
            self.title = 'cmus {status}'.format(**self.tags)

            if self.tags['track']:
                self.subtitle += '{track}) '.format(**self.tags)

            if self.tags['title']:
                self.subtitle += '{title}'.format(**self.tags)

            if self.tags['artist']:
                self.message += '{artist}'.format(**self.tags)

            if self.tags['album']:
                self.message += '\n{album}'.format(**self.tags)

            if self.tags['date']:
                self.message += ' ({date})'.format(**self.tags)


#------------------------------------------------------------------------------
class Notification:
    def __init__(self):
        pass

    def show(self, title, subtitle, message):
        center = NSUserNotificationCenter.defaultUserNotificationCenter()
        notification = NSUserNotification.alloc().init()

        notification.setTitle_(title)
        notification.setSubtitle_(subtitle.decode('utf-8'))
        notification.setInformativeText_(message.decode('utf-8'))

        if ICON_PATH:
            img = AppKit.NSImage.alloc().initByReferencingFile_(ICON_PATH)
            notification.setContentImage_(img)

        if DISPLAY_MODE == 1:
            notification.setIdentifier_('cmus')
        elif DISPLAY_MODE == 2:
            center.removeAllDeliveredNotifications()

        center.deliverNotification_(notification)


#------------------------------------------------------------------------------
class OptionLoader():
       def __init__(self):
           if UPDATE_OPTIONS_FROM_CONFIG is False:
               return # simply do nothing

           with open(CMUS_OSX_CONFIG, "r") as jfile:
               root = json.load(jfile)
               if 'notify' in root:
                   notify = root['notify']
                   if 'mode' in notify:
                       global DISPLAY_MODE
                       DISPLAY_MODE = notify['mode']

                   if 'icon_path' in notify:
                       global ICON_PATH
                       ICON_PATH = notify['icon_path']


#------------------------------------------------------------------------------
if __name__ == '__main__':
    OptionLoader()
    if DISPLAY_MODE == 0:
        sys.exit(1) # do nothing and quit

    cmus = CmusArguments(sys.argv)
    cmus.make()
    if cmus.title:
        noti = Notification()
        noti.show(cmus.title, cmus.subtitle, cmus.message)

