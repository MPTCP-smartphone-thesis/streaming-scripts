#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
#  Copyright 2015 Matthieu Baerts & Quentin De Coninck
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import logging
logging.basicConfig(level=logging.DEBUG)


##################################
##            PARSER            ##
##################################

import database as mdb
import argparse

parser = argparse.ArgumentParser(description="Generate map image with dots where a connection has been changed")
parser.add_argument("-I", "--db-ip", help="MongoDB's IP address", default=mdb.DB_IP)
parser.add_argument("-P", "--db-port", type=int, help="MongoDB's port", default=mdb.DB_PORT)
parser.add_argument("-N", "--db-name", help="MongoDB's DB name", default=mdb.DB_NAME)
parser.add_argument("wlan", help="WLan MAC address")
parser.add_argument("timestart", type=int, help="Start: from this timestamp")
parser.add_argument("timeend", type=int, help="End: to this timestamp")
# https://wiki.openstreetmap.org/wiki/Zoom_levels
parser.add_argument("-z", "--zoom", type=int, help="Zoom level for the map", default=18)
parser.add_argument("-o", "--output", help="Output file")


##################################
##            IMPORT            ##
##################################

import numpy as np

import matplotlib.pyplot as plt
import geotiler


##################################
##             MAP              ##
##################################

CIRC = 2 * np.pi * 6372798.2 # ~= 40km

def get_meter_by_pixel(lat, zoom):
    return CIRC * np.cos(np.radians(lat)) / 2**(zoom+8)

def get_point_size(meters, mbp):
    return meters / mbp

class Map(object):
    def __init__(self, wlan, time_start, time_end, zoom=18, db_ip=mdb.DB_IP, db_port=mdb.DB_PORT, db_name=mdb.DB_NAME):
        bbox = None
        with mdb.Database(db_ip, db_port, db_name) as db:
            pos_infos = db.get_position(wlan, time_start, time_end)

        count = pos_infos.count()
        if count < 2:
            raise Exception("No position info: " + str(count))
        self.points, self.acc, self.annot, bbox = self.__get_info(pos_infos)

        self.mm = geotiler.Map(extent=bbox, zoom=zoom)
        self.mbp = get_meter_by_pixel(self.mm.center[1], zoom)

    def __get_info(self, pos_infos):
        min_lat = 90.
        max_lat = -90.
        min_lon = 180.
        max_lon = -180.

        points = []
        acc = []
        annot = []
        for info in pos_infos:
            lat = info['posLatitude']
            lon = info['posLongitude']
            accuracy = info['posAccuracy']
            if accuracy > 200:
                logging.warn("Not good accuracy: " + str(accuracy) + " - " + str((lon, lat)))
                continue

            min_lat = min(min_lat, lat)
            max_lat = max(max_lat, lat)
            min_lon = min(min_lon, lon)
            max_lon = max(max_lon, lon)
            logging.debug("Pts: " + str(accuracy) + " - " + str((lon, lat)))

            points.append((lon, lat))
            acc.append(accuracy)
            annot.append(info['netType']) # TODO annotate

        bbox = min_lon, min_lat, max_lon, max_lat
        return points, acc, annot, bbox

    def __get_coord_meters(self):
        x = []
        y = []

        for pt in self.points:
            pos = self.mm.rev_geocode(pt)
            x.append(pos[0]) # TODO: *self.mbp: in meter but *map size
            y.append(pos[1])

        return x, y

    def draw(self, filename):
        logging.debug('acc before: ' + str(self.acc))
        self.acc = tuple((np.array(self.acc) / self.mbp / 2) ** 2) # accuracy in pixel
        logging.debug('acc after: ' + str(self.acc))

        x, y = self.__get_coord_meters()
        logging.debug((x, y))

        # fig = plt.figure(figsize=(10, 10))
        ax = plt.subplot(111)

        img = geotiler.render_map(self.mm)
        ax.imshow(img)

        ax.scatter(x, y, c='red', edgecolor='red', s=self.acc, alpha=0.1)
        ax.plot(x, y)
        for i, txt in enumerate(self.annot):
            ax.annotate(txt, (x[i],y[i]))

        plt.savefig(filename, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    args = parser.parse_args()
    mm = Map(args.wlan, args.timestart, args.timeend, args.zoom, args.db_ip, args.db_port, args.db_name)
    if args.output:
        filename = args.output
    else:
        import time
        filename = "export/map_" + args.wlan + "_" + time.strftime("%Y%m%d-%H%M%S") + ".pdf"
    mm.draw(filename)
    print("File exported to: " + filename)
