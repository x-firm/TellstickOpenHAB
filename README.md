TellstickOpenHAB
================

Integration example of using Tellstick Duo and openHAB for home automation.

This compilation depends on the python library for tellstick, 'tellcore.telldus'. It must be installed on on the machine that runs these scripts. Also the original telldus tellcore libraries needs to be installed.

This particular setup runs on a Raspberry PI, but nothing is PI specific.

Included is a python script (tellstick/tellstick-openhab.py) that sends REST requests to openHAB to notify of tellstick events not currently picked up by the openHAB tellstick binding. 
Some modifications to this file is currently needed. Modifictaions include adding your own devices according to the pattern in the file. Also if openHAB is running on another machine the base URL to that machine must also be updated. Default is 'locslhost:8080'. The path to where the 'tellstick-openhab.py' file must also be updated.


Also included is a Linux service (init.d/openhab-tellstick) that starts a daemon running above mentioned python script, this should be copied to /etc/init.d.


The tellstick sevice should be started FIRST then the openhab-tellstick service, otherwise destruction and mayhem are likely!

The tellstick ID's in the tellstick.item file can be found using the tellcore_tool as below:

pi@raspberrypi00 ~ $ tellcore_tool -l

Number of devices: 9

ID    NAME            STATE      PROTOCOL   MODEL                PARAMETERS
1     Example device  OFF        arctech    codeswitch           house:A unit:1 
2     MagSwitch       OFF        arctech    selflearning         house:9837886 unit:10 
3     Motion sensor   OFF        arctech    selflearning         house:9538298 unit:10 
4     Lamp 1          OFF        arctech    selflearning-switch  house:9091782 unit:1 
5     Lamp 2          OFF        arctech    selflearning-switch  house:9091782 unit:2 
6     Lamp 3          OFF        arctech    selflearning-switch  house:9091782 unit:3 
7     Guestroom Lamp  OFF        arctech    selflearning-switch  house:47114711 unit:3 
8     Office Desk Lamp OFF        arctech    selflearning-switch  house:9737326 unit:1 
9     Tea Lamp        OFF        arctech    selflearning-switch  house:12617438 unit:1 

Number of sensors: 19

PROTOCOL        MODEL           ID    TEMP     HUMIDITY RAIN               WIND                 LAST UPDATED
fineoffset      temperature     255   -204.7 C                                                  2014-09-01 19:49:05
mandolyn        temperaturehumidity 22    22.9 C   48 %                                             2014-09-01 19:49:55
mandolyn        temperaturehumidity 21    23.1 C   46 %                                             2014-09-01 19:49:50
mandolyn        temperaturehumidity 11    22.6 C   47 %                                             2014-09-01 19:15:34
fineoffset      temperaturehumidity 2     0.0 C    0 %                                              2014-09-01 05:10:58
fineoffset      temperaturehumidity 255   0.0 C    0 %                                              2014-09-01 19:29:55
mandolyn        temperaturehumidity 1     -14.8 C  0 %                                              2014-08-31 11:06:56
fineoffset      temperaturehumidity 254   0.0 C    0 %                                              2014-08-30 02:11:04
fineoffset      temperaturehumidity 0     0.0 C    0 %                                              2014-08-31 20:22:58
mandolyn        temperaturehumidity 84    102.6 C  73 %                                             2014-08-22 14:12:30
fineoffset      temperaturehumidity 1     0.0 C    0 %                                              2014-08-25 23:09:17
mandolyn        temperaturehumidity 124   206.0 C  127 %                                            2014-08-22 22:08:28
fineoffset      temperaturehumidity 6     0.0 C    0 %                                              2014-09-01 03:01:58
fineoffset      temperature     0     51.1 C                                                    2014-08-30 08:35:00
fineoffset      temperaturehumidity 16    0.0 C    1 %                                              2014-08-30 04:23:00
fineoffset      temperature     63    -204.7 C                                                  2014-08-30 08:49:00
oregon          EA4C            229   14.8 C                                                    2014-09-01 19:50:05
mandolyn        temperaturehumidity 154   206.0 C  127 %                                            2014-08-31 09:42:00
fineoffset      temperaturehumidity 30    0.0 C    0 %                                              2014-09-01 05:19:59


New devices can be identified using the tellcore_events tool thusly:

pi@raspberrypi00 ~ $ tellcore_events --all

[RAW] 1 <- class:command;protocol:waveman;model:codeswitch;house:A;unit:1;method:turnoff;
[RAW] 1 <- class:sensor;protocol:fineoffset;id:255;model:temperature;temp:-204.7;
[SENSOR] 255 [fineoffset/temperature] (1) @ 1409595745 <- -204.7
[RAW] 1 <- class:sensor;protocol:oregon;model:EA4C;id:229;temp:13.4;
[SENSOR] 229 [oregon/EA4C] (1) @ 1409595755 <- 13.4

This can be used to find the parameters to add in the tellstick-openhab.py script.


TODO:

Extract devices definition from tellstick-openhab.py to a config file. 
Create script that builds a config file using output from tellcore_events.


