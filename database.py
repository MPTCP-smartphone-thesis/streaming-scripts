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

from pymongo import MongoClient
import os
import subprocess
import time

DB_IP = "localhost"
DB_PORT = 27017
DB_NAME = "mpctrl"

class Database(object):
    def __init__(self, ip=DB_IP, port=DB_PORT, db_name=DB_NAME, db_connect=False):
        if db_connect and os.path.exists('mongo.sh') and not os.path.exists('mongo.sh.skip'):
            self.proc = subprocess.Popen(['./mongo.sh'])
            time.sleep(2)
        else:
            self.proc = None
        self.connection = MongoClient(host=ip, port=port)
        self.db = self.connection[db_name]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.connection.close()
        if self.proc:
            self.proc.kill()

    def get_position(self, wifi_mac, timestamp_start, timestamp_end):
        return self.db.handover.find(
            {
                'wifiMac': wifi_mac,
                'timestamp': {"$gt": timestamp_start, "$lt": timestamp_end}
            },
            ['ifaces', 'ipRMNet4', 'ipWifi4', 'netReason', 'netType',
             'posLatitude', 'posLongitude', 'posAccuracy',
             'wifiSignalRSSI', 'wifiBSSID']
            ).sort('timestamp')
