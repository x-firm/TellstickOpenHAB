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
remote_control            = {'name':'SimpleRemote',       'model': 'selflearning', 'protocol': 'arctech', 'house': 9091782, 'unit':1, 'group':0};
motion_detector           = {'name':'MotionDetectorHall', 'model': 'selflearning', 'protocol': 'arctech', 'house': 9538298, 'unit':10, 'group':0};
motion_detector_out       = {'name':'MotionDetectorOut',  'model': 'selflearning', 'protocol': 'arctech', 'house': 8776650, 'unit':10, 'group':0};
magnetic_switch_cellar_C  = {'name':'MagSwitchCellar',    'model': 'selflearning', 'protocol': 'arctech', 'house': 23188454, 'unit':15, 'group':0};
magnetic_switch_cellar_D  = {'name':'MagSwitchCellar',    'model': 'selflearning', 'protocol': 'arctech', 'house': 9837886, 'unit':10, 'group':0};
magnetic_switch_door_C    = {'name':'MagSwitchFrontDoor', 'model': 'selflearning', 'protocol': 'arctech', 'house': 13742794, 'unit':10, 'group':0};
magnetic_switch_door_D    = {'name':'MagSwitchFrontDoor', 'model': 'selflearning', 'protocol': 'arctech', 'house': 18558118, 'unit':10, 'group':0};
dusk_detector             = {'name':'DuskDetector',       'model': 'selflearning', 'protocol': 'arctech', 'house': 8927022, 'unit':10, 'group':0};


devices = {9538298: motion_detector,
           8776650: motion_detector_out,
           23188454: magnetic_switch_cellar_C,
           9837886: magnetic_switch_cellar_D,
           13742794: magnetic_switch_door_C,
           18558118: magnetic_switch_door_D,
           9091782: remote_control,
           8927022: dusk_detector}


id_dev  = {23188454: 9837886}
id_unit = {23188454: 10}
id_dev  = {13742794: 18558118}
id_unit = {13742794: 10}

value_mapping = {9538298: {'turnon':'OPEN', 'turnoff':'CLOSED'},
           8776650: {'turnon':'OPEN', 'turnoff':'CLOSED'},
           23188454: {'turnon':'OPEN', 'turnoff':'CLOSED'},
           9091782: {'turnon':'ON', 'turnoff':'OFF'},
           8927022: {'turnon':'OPEN', 'turnoff':'CLOSED'},
           13742794: {'turnon':'OPEN', 'turnoff':'CLOSED'},
           18558118: {'turnon':'OPEN', 'turnoff':'CLOSED'},
           9837886: {'turnon':'OPEN', 'turnoff':'CLOSED'}} 


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
        core.callback_dispatcher.process_pending_callbacks()
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

