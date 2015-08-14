
import math
import time
from datetime import datetime
import ephem
import numpy as np
import matplotlib.pyplot as plt
import sys
import os.path
import zipfile
import urllib
import urllib2

degree_sign = u'\N{DEGREE SIGN}'

# http://www.celestrak.com/NORAD/elements/
 
# import tle data from NORAD if internet_on(), save as sat=ephem.readtle(...)-----


def internet_on():
    try:
        urllib2.urlopen('http://google.com', timeout=1)   # tries to contact Google
        return True
    except: pass
    return False


if internet_on():
    myfile = urllib.URLopener()
    myfile.retrieve('http://www.tle.info/data/ALL_TLE.ZIP', 'ALL_TLE.ZIP')
    print 'ALL_TLE.ZIP updated.'
else:
    print 'Connection unavailable. Using saved ALL_TLE.ZIP (' + time.ctime(os.path.getmtime('ALL_TLE.ZIP')) + ')'
content = []
 
print 'Unzipping ALL_TLE.ZIP...'
azip = zipfile.ZipFile('ALL_TLE.ZIP')
azip.extractall('.')
print "Done unzipping"

# load TLE data into python array
with open('ALL_TLE.TXT') as f:
    content = f.readlines()
    print int(len(content) /  3), 'TLEs loaded from ALL_TLE.TXT.'
    for i in range(0, len(content)):
        content[i] = content[i].replace('\n', '')   # remove endlines
         
         
# Set observer location
home = ephem.Observer()
locationKeyword = raw_input('Location keyword: ')   # type first few letters of the location keywords included in the entries below
locationName = ''

if locationKeyword.lower() == 'abilene'[0:len(locationKeyword)].lower():
    locationName = 'Abilene, TX'
    print 'Observer in Abilene, TX.'
    home = ephem.Observer()
    home.lon = '-99.74'         # +E
    home.lat = '32.45'          # +N
    home.elevation = 524.0      # meters
    # home.temp = 38.0          # deg Celcius
    # home.pressure = 1016.0    # mbar

elif locationKeyword.lower() == 'college station'[0:len(locationKeyword)].lower():
    locationName = 'College Station, TX'
    print 'Observer in College Station, TX.'
    home = ephem.Observer()
    home.lon = '-96.314444'     # +E
    home.lat = '30.601389'      # +N
    home.elevation = 103.0      # meters
    # home.temp = 26.0          # deg Celcius
    # home.pressure = 0.0       # mbar

elif locationKeyword.lower() == 'oxford'[0:len(locationKeyword)].lower():
    locationName = 'Oxford, England'
    print 'Observer in Oxford, England.'
    home = ephem.Observer()
    home.lon = '-1.2578'        # +E
    home.lat = '51.7519'        # +N
    home.elevation = 72.0       # meters
    # home.temp = 26.0          # deg Celcius
    # home.pressure = 0.0       # mbar

elif locationKeyword.lower() == 'bristol'[0:len(locationKeyword)].lower():
    locationName = 'Bristol, RI'
    print 'Observer in Bristol, RI.'
    home = ephem.Observer()
    home.lon = '-71.2686'       # +E
    home.lat = '41.6842'        # +N
    home.elevation = 40.0       # meters
    # home.temp = 26.0          # deg Celcius
    # home.pressure = 0.0       # mbar
 
else:
    print 'Location keyword not found.'
    sys.exit()


# read in each # tle entry and save to list
savedsats = []
satnames = []
i_name = 0
while 3 * i_name + 2 <= len(content):
    # for each satellite in the content list...
    savedsats.append(ephem.readtle(content[3 * i_name], content[3 * i_name + 1], content[3 * i_name + 2]))
    satnames.append(content[3 * i_name])
    i_name += 1
 
fig = plt.figure()
 
t = time.time()
print t
while 1:
    fig.clf()
    home.date = datetime.utcnow()
 
    theta_plot = []
    r_plot = []
     
    # click on a satellite to print its TLE name to the console
    def onpick(event):
        global t
        if time.time() - t < 1.0:   # limits calls to 1 per second
            return
        t = time.time()
        ind = event.ind
        r = np.take(r_plot, ind)[0]
        theta = np.take(theta_plot, ind)[0]
        i = 0
        while i < len(savedsats) and (math.degrees(theta) != math.degrees(savedsats[i].az) or math.cos(savedsats[i].alt) != r):
            i += 1
        print satnames[i], 'az=' + str(math.degrees(savedsats[i].az)), 'alt=' + str(math.degrees(savedsats[i].alt))
 
         
    for sat in savedsats:   # for each satellite in the savedsats list...
        sat.compute(home)
        if math.degrees(sat.alt) > 0.0:
            theta_plot.append(sat.az)
            r_plot.append(math.cos(sat.alt))
                 
    # plot initialization and display
    ax = plt.subplot(111, polar = True)
    ax.set_theta_direction(-1)      # clockwise
    ax.set_theta_offset(np.pi / 2)  # put 0 degrees (north) at top of plot
    ax.yaxis.set_ticklabels([])     # hide radial tick labels
    ax.grid(True)
    title = str(home.date)
    ax.set_title(title, va = 'bottom')
    ax.scatter(theta_plot, r_plot, picker = True)
    fig.canvas.mpl_connect('pick_event', onpick)
    ax.set_rmax(1.0)
    plt.pause(1.0)
