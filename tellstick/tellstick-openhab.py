#!/usr/bin/env python

import re
import sys
import time

from time import gmtime, strftime

import tellcore.telldus as td
from tellcore.constants import *

import httplib

logfile = open('/var/log/openhab-tellstick.log', 'a+') 

# Known raw devices

magnetic_switch_kitchen_C  = {'name':'MagSwitchKitchen',    'model': 'selflearning', 'protocol': 'arctech', 'house': 48801126, 'unit':1, 'group':0};
magnetic_switch_kitchen_D  = {'name':'MagSwitchKitchen',    'model': 'selflearning', 'protocol': 'arctech', 'house': 15632982, 'unit':10, 'group':0};


devices = {48801126: magnetic_switch_kitchen_C,
           15632982: magnetic_switch_kitchen_D}


id_dev  = {48801126: 15632982}
id_unit = {48801126: 1}


value_mapping = {48801126: {'turnon':'OPEN', 'turnoff':'CLOSED'},
                 15632982: {'turnon':'OPEN', 'turnoff':'CLOSED'}}


print "Devices are:"
print devices

protocol_wdata_re = re.compile('class:command;protocol:([^;]+);model:selflearning;house:(\d+);unit:(\d+);group:(\d+);method:([^;]+); <- (.+)')

openhab = "localhost:8080"
headers = {"Content-type": "text/plain"}
connErr = "No connection to openhab on http://" + openhab

METHODS = {TELLSTICK_TURNON: 'ON',
           TELLSTICK_TURNOFF: 'OFF',
           TELLSTICK_BELL: 'BELL',
           TELLSTICK_TOGGLE: 'toggle',
           TELLSTICK_DIM: 'dim',
           TELLSTICK_LEARN: 'learn',
           TELLSTICK_EXECUTE: 'execute',
           TELLSTICK_UP: 'up',
           TELLSTICK_DOWN: 'down',
           TELLSTICK_STOP: 'stop'}

def eventlog(logmsg):
    logfile.write("Tellstick event {0}: ".format(strftime("%Y-%m-%d %H:%M:%S")))
    logfile.write(logmsg)
    logfile.write("\n")
    logfile.flush()

def raw_event(data, controller_id, cid):
    protocol_string = "{1} <- {0}".format(controller_id, data)
    m = protocol_wdata_re.match(protocol_string)    
    if(m):
        print m.groups()
        dev = devices.get(int(m.group(2)))
        if(dev):
            print "Dev is {0} House: {1}".format(dev['name'],dev['house'])
            if(id_dev.get(dev['house'])):
                house_id = id_dev.get(dev['house'])
                unit_id  = id_unit.get(dev['house'])
            else:
                house_id = dev['house']
                unit_id  = dev['unit']
            url = "/rest/items/{0}/state".format(dev['name'],house_id,unit_id,dev['group'])
            value = 0
            value_m = value_mapping.get(dev['house'])
            if(value_m):
                value = value_m.get(m.group(5)) 
            else:
                value = m.group(5)
            try:
                conn = httplib.HTTPConnection(openhab)
                conn.request('PUT', url, value, headers)
                eventlog("{0} => {1}".format(dev['name'],value))
            except:
                print(connErr)
    string = "[RAW] {0} <- {1}".format(controller_id, data)
    print(string)

def device_event(id_, method, data, cid):
    method_string = METHODS.get(method, "UNKNOWN STATE {0}".format(method))
    string = "[DEVICE] {0} -> {1}".format(id_, method_string)
    if method == TELLSTICK_DIM:
        string += " [{0}]".format(data)
    print(string)
    url = "/rest/items/td_device_{0}/state".format(id_)
    try:
        conn = httplib.HTTPConnection(openhab)
        conn.request('PUT', url, method_string, headers)
    except:
        print(connErr)

def sensor_event(protocol, model, id_, dataType, value, timestamp, cid):
    string = "[SENSOR] {0} [{1}/{2}] ({3}) @ {4} <- {5}".format(
        id_, protocol, model, dataType, timestamp, value)
    print(string)
    #url = "/rest/items/td_sensor_{0}_{1}_{2}/state".format(protocol, id_, dataType)
    #try:
    #    conn = httplib.HTTPConnection(openhab)
    #    conn.request('PUT', url, value, headers)
    #except:
    #    print(connErr)

core = td.TelldusCore()
callbacks = []

callbacks.append(core.register_device_event(device_event))
callbacks.append(core.register_raw_device_event(raw_event))
callbacks.append(core.register_sensor_event(sensor_event))

try:
    while True:
        core.process_pending_callbacks()
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

