
import math
import time
from datetime import datetime
import ephem
import numpy as np
import matplotlib.pyplot as plt
import zipfile
import urllib

degree_sign = u'\N{DEGREE SIGN}'


def download_tle():
    """ downloads the "ALL_TLE" file from the tle info server """

    myfile = urllib.URLopener()
    myfile.retrieve('http://www.tle.info/data/ALL_TLE.ZIP', 'ALL_TLE.ZIP')
    azip = zipfile.ZipFile('ALL_TLE.ZIP')
    azip.extractall('.')
    print("TLE data obtained!")

    # load TLE data into python array
    with open('ALL_TLE.TXT') as f:
        tle_content = f.readlines()
        tle_content = [line.replace('\n', '') for line in tle_content]  # remove end lines
        print("loaded {0} TLEs".format(int(len(tle_content) /  3)))

    return tle_content


def set_observer(lat, lon, elevation):
    """
    :param lat: latitude of observer in degrees North
    :param lon: longitude of observer in degrees East
    :param elevation: elevation of observer in meters
    :return: ephem.Observer() object for input location
    """
    home = ephem.Observer()
    home.lat = lat
    home.lon = lon
    home.elevation = elevation
    return home


def plot_observer_view(lat, lon, elevation):
    """
    :param lat: latitude of observer in degrees North
    :param lon: longitude of observer in degrees East
    :param elevation: elevation of observer in meters
    :return:
    """

    content = download_tle()
    home = set_observer(lat, lon, elevation)

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
    print(t)

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
            print(satnames[i], 'az=' + str(math.degrees(savedsats[i].az)), 'alt=' + str(math.degrees(savedsats[i].alt)))


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


if __name__ == "__main__":
    plot_observer_view(36, -76.3601, 3)