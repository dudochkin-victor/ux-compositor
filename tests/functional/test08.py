#!/usr/bin/python

# Check that a transient dialog is raised with the application it is
# transient for.

#* Test steps
#  * show an application window
#  * create and show a dialog window that is transient for the application
#  * iconify the application window
#  * activate the application window
#  * check that the transient is above the application window
#  * iconify the application window
#  * activate the transient window
#  * check that the transient is above the application window
#  * create and show a dialog window that is transient for the previous dialog
#  * iconify the application window
#  * activate the application window
#  * check that both transients are above the application window and in order
#  * swap the transiencies of the dialogs
#* Post-conditions
#  * check that both transients are above the application window and in order

import os, re, sys, time

if os.system('mcompositor-test-init.py'):
  sys.exit(1)

fd = os.popen('windowstack m')
s = fd.read(5000)
win_re = re.compile('^0x[0-9a-f]+')
home_win = 0
for l in s.splitlines():
  if re.search(' DESKTOP viewable ', l.strip()):
    home_win = win_re.match(l.strip()).group()

if home_win == 0:
  print 'FAIL: desktop window not found'
  sys.exit(1)

# create application and transient dialog windows
fd = os.popen('windowctl kn')
old_win = fd.readline().strip()
time.sleep(1)
fd = os.popen("windowctl kd %s" % old_win)
new_win = fd.readline().strip()
time.sleep(1)

# iconify the application
os.popen("windowctl O %s" % old_win)
time.sleep(2)

# activate the application (this should raise the dialog too)
os.popen("windowctl A %s" % old_win)
time.sleep(1)

ret = new_win_found = 0
fd = os.popen('windowstack m')
s = fd.read(5000)
for l in s.splitlines():
  if re.search("%s " % new_win, l.strip()):
    print new_win, 'found'
    new_win_found = 1
  elif re.search("%s " % old_win, l.strip()) and new_win_found:
    print old_win, 'found'
    break
  elif re.search("%s " % old_win, l.strip()):
    print 'FAIL: app is stacked before dialog'
    print 'Failed stack:\n', s
    ret = 1
    break
  elif re.search("%s " % home_win, l.strip()):
    print 'FAIL: home is stacked before app'
    print 'Failed stack:\n', s
    ret = 1
    break

# iconify the application
os.popen("windowctl O %s" % old_win)
time.sleep(2)

# activate the transient
os.popen("windowctl A %s" % new_win)
time.sleep(1)

new_win_found = 0
fd = os.popen('windowstack m')
s = fd.read(5000)
for l in s.splitlines():
  if re.search("%s " % new_win, l.strip()):
    print new_win, 'found'
    new_win_found = 1
  elif re.search("%s " % old_win, l.strip()) and new_win_found:
    print old_win, 'found'
    break
  elif re.search("%s " % old_win, l.strip()):
    print 'FAIL: app is stacked before dialog'
    print 'Failed stack:\n', s
    ret = 1
    break
  elif re.search("%s " % home_win, l.strip()):
    print 'FAIL: home is stacked before app'
    print 'Failed stack:\n', s
    ret = 1
    break

# create a dialog that is transient to the first dialog
fd = os.popen("windowctl kd %s" % new_win)
new_dialog = fd.readline().strip()
time.sleep(1)

# iconify the application
os.popen("windowctl O %s" % old_win)
time.sleep(2)

# activate the application (this should raise the dialogs too)
os.popen("windowctl A %s" % old_win)
time.sleep(1)

new_dialog_found = new_win_found = 0
fd = os.popen('windowstack m')
s = fd.read(5000)
for l in s.splitlines():
  if re.search("%s " % new_dialog, l.strip()):
    print new_dialog, 'found'
    new_dialog_found = 1
  elif re.search("%s " % new_win, l.strip()) and new_dialog_found:
    print new_win, 'found'
    new_win_found = 1
  elif re.search("%s " % new_win, l.strip()):
    print 'FAIL: old dialog is stacked before new dialog'
    print 'Failed stack:\n', s
    ret = 1
    break
  elif re.search("%s " % home_win, l.strip()):
    print 'FAIL: home is stacked before app'
    print 'Failed stack:\n', s
    ret = 1
    break
  elif re.search("%s " % old_win, l.strip()) and new_dialog_found \
       and new_win_found:
    print old_win, 'found'
    break
  elif re.search("%s " % old_win, l.strip()):
    print 'FAIL: app is stacked before a transient dialog'
    print 'Failed stack:\n', s
    ret = 1
    break

# get the root window and the current stacking
r = re.compile("Window id: (0x[0-9a-fA-F]*)")
root = [ m.group(1) for m in [ r.search(l) for l in os.popen("xwininfo -root") ]
	if m is not None ][0]
rnwmclist = re.compile('^_NET_CLIENT_LIST_STACKING:')
stacking = filter(rnwmclist.match, os.popen("xprop -id %s -notype" % root))[0]

# swap the transiencies of the dialogs
# (this introduces a temporary transiency loop)
os.popen("windowctl t %s %s" % (new_win, new_dialog))
os.popen("windowctl t %s %s" % (new_dialog, old_win))

# wait until the wm has restacked
prev_stacking = stacking
while stacking == prev_stacking:
	time.sleep(0.5)
	prev_stacking = stacking
	stacking = filter(rnwmclist.match,
		os.popen("xprop -id %s -notype" % root))[0]

new_dialog_found = new_win_found = 0
fd = os.popen('windowstack m')
s = fd.read(5000)
for l in s.splitlines():
  if re.search("%s " % new_win, l.strip()):
    print new_win, 'found'
    new_win_found = 1
  elif re.search("%s " % new_dialog, l.strip()) and new_win_found:
    print new_dialog, 'found'
    new_dialog_found = 1
  elif re.search("%s " % new_dialog, l.strip()):
    print 'FAIL: lower dialog is stacked before the upper dialog'
    print 'Failed stack:\n', s
    ret = 1
    break
  elif re.search("%s " % home_win, l.strip()):
    print 'FAIL: home is stacked before app'
    print 'Failed stack:\n', s
    ret = 1
    break
  elif re.search("%s " % old_win, l.strip()) and new_dialog_found \
       and new_win_found:
    print old_win, 'found'
    break
  elif re.search("%s " % old_win, l.strip()):
    print 'FAIL: app is stacked before a transient dialog'
    print 'Failed stack:\n', s
    ret = 1
    break

# cleanup
os.popen('pkill windowctl')
time.sleep(1)

if os.system('/usr/bin/gconftool-2 --type bool --set /desktop/meego/notifications/previews_enabled true'):
  print 'cannot re-enable notifications'

sys.exit(ret)
