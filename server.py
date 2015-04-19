#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="vitaliy"
__date__ ="$Sep 9, 2014 12:40:24 AM$"

#!/usr/bin/env python
import string,cgi,time,pprint,serial,sys,smbus,time,json
from time import localtime, strftime
from os import curdir, sep
from urlparse import urlparse, parse_qs
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from daemon import Daemon
import pylcdlib
import datetime

BATHROOM_LCD = 0x25;
SOUND_LCD = 0x26;

PT2323_ADDRESS  = 74      #7 bit address (will be left shifted to add the read write bit)
PT2258_ADDRESS  = 68
DEVICE_REG_MODE1 = 0x00
DEVICE_REG_LEDOUT0 = 0x1d

MIN_ATTENUATION = 0
MAX_ATTENUATION = 79

CHAN_ALL  =  0
CHAN_FL   =  1
CHAN_FR   =  2
CHAN_RL   =  3
CHAN_RR   =  4
CHAN_SW   =  5
CHAN_CEN  =  6

PT2258_FL_1DB     =  0x90
PT2258_FL_10DB    =  0x80
PT2258_FR_1DB     =  0x50
PT2258_FR_10DB    =  0x40
PT2258_RL_1DB     =  0x70
PT2258_RL_10DB    =  0x60
PT2258_RR_1DB     =  0xB0
PT2258_RR_10DB    =  0xA0
PT2258_CEN_1DB    =  0x10
PT2258_CEN_10DB   =  0x00
PT2258_SW_1DB     =  0x30
PT2258_SW_10DB    =  0x20
PT2258_ALLCH_1DB  =  0xE0
PT2258_ALLCH_10DB =  0xD0

volumeFR = 0
volumeFL = 0
volumeRR = 0 
volumeRL = 0 
volumeCEN = 0
volumeSW = 0 
volumeALLCH = 0 


bus = smbus.SMBus(1)


global chips
global lampbits
global chipstate

chips = [
		0x3d,0x3d,0x3d,0x3d,0x3d,0x3d,0x3d,0x3d,
		0x21,0x21,0x21,0x21,0x21,0x21,0x21,0x21,
		0x22,0x22,0x22,0x22,0x22,0x22,0x22,0x22,
		0x23,0x23,0x23,0x23,0x23,0x23,0x23,0x23,
		0x27,0x27,0x27,0x27,0x27,0x27,0x27,0x27
	]

lampbits = [
		7,6,5,4,3,2,1,0,
		7,6,5,4,3,2,1,0,
		7,6,5,4,3,2,1,0,
		7,6,5,4,3,2,1,0,
		7,6,5,4,3,2,1,0
           ]

chipstate = { 0x3d:0x00, 0x21:0x00, 0x22:0x00, 0x23:0x00, 0x27:0x00 }

def chipForLamp(position):
    global chips
    return chips[position]

def setBit(int_type, offset):
    mask = 1 << offset
    return(int_type | mask)

def clearBit(int_type, offset):
    mask = ~(1 << offset)
    return(int_type & mask)
 
def toggleBit(int_type, offset):
    mask = 1 << offset
    return(int_type ^ mask)

def lampBit(position):
    global lampbits
    return lampbits[position]

def writeLigthState():
    global chipstate
    for chip, state in chipstate.items():
       bus.write_byte(chip, state)
       print chip, " ", state


def toggleLamp(position):
    global chipstate
    chip = chipForLamp(position)
    chipstate[chip] = toggleBit(chipstate[chip],lampBit(position))
    writeLigthState()


def enableLamp(position):
    global chipstate
    chip = chipForLamp(position)
    chipstate[chip] = setBit(chipstate[chip],lampBit(position))
    writeLigthState()


def disableLamp(position):
    global chipstate
    chip = chipForLamp(position)
    chipstate[chip] = clearBit(chipstate[chip],lampBit(position))
    writeLigthState()

def allOn():
    global chipstate
    chipstate[0x3d] = 255;
    chipstate[0x21] = 255;
    chipstate[0x22] = 255;
    chipstate[0x23] = 255;
    chipstate[0x27] = 255;
    writeLigthState()

def allOff():
    global chipstate
    chipstate[0x3d] = 0;
    chipstate[0x21] = 0;
    chipstate[0x22] = 0;
    chipstate[0x23] = 0;
    chipstate[0x27] = 0;
    writeLigthState()

def lampState():
    global chipstate

    return json.dumps(chipstate)
    return json.dumps([
                chipstate[0x3d],
                chipstate[0x21],
                chipstate[0x22],
                chipstate[0x23],
                chipstate[0x27]
                ])


def pt2258(channel, value):

    global volumeFR
    global volumeFL
    global volumeRR
    global volumeRL
    global volumeCEN
    global volumeSW
    global volumeALLCH

    global chips
    global lampbits
    global chipstate

    if channel == CHAN_ALL:
       volumeALLCH = value
       volumeFR = value
       volumeFL = value
       volumeRR = value
       volumeRL = value
       volumeCEN = value
       volumeSW = value
       volumeALLCH = value


       x10 =  PT2258_ALLCH_10DB + (value / 10);
       x1 =   PT2258_ALLCH_1DB + (value % 10);

    if channel == CHAN_FR:
       volumeFR = value
       x10 =  PT2258_FR_10DB + (value / 10);
       x1 =   PT2258_FR_1DB + (value % 10);

    if channel == CHAN_FL:
       volumeFL = value
       x10 =  PT2258_FL_10DB + (value / 10);
       x1 =   PT2258_FL_1DB + (value % 10);

    if channel == CHAN_RR:
       volumeRR = value
       x10 =  PT2258_RR_10DB + (value / 10);
       x1 =   PT2258_RR_1DB + (value % 10);

    if channel == CHAN_RL:
       volumeRL = value
       x10 =  PT2258_RL_10DB + (value / 10);
       x1 =   PT2258_RL_1DB + (value % 10);

    if channel == CHAN_CEN:
       volumeCEN = value
       x10 =  PT2258_CEN_10DB + (value / 10);
       x1 =   PT2258_CEN_1DB + (value % 10);

    if channel == CHAN_SW:
       volumeSW = value
       x10 =  PT2258_SW_10DB + (value / 10);
       x1 =   PT2258_SW_1DB + (value % 10);

#    print channel
#    print value
#    print x10
#    print x1

    bus.write_byte_data(PT2258_ADDRESS,x1,x10)
#    return 
    return json.dumps({
		'FR'  :74-volumeFR,
		'FL'  :74-volumeFL,
		'RR'  :74-volumeRR,
		'RL'  :74-volumeRL,
		'CEN' :74-volumeCEN,
		'SW'  :74-volumeSW,
		'ALL' :74-volumeALLCH
		})

def pt2323(command):
    bus.write_i2c_block_data(PT2323_ADDRESS, DEVICE_REG_MODE1, command)


def writeLcdLine(adress,text,line):
    lcd = pylcdlib.lcd(bus, adress,1)
    lcd.lcd_write(0x01);
    lcd.lcd_puts(text,line)
    lcd.lcd_backlight(1)



class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
	     global volumeFR
             global volumeFL
             global volumeRR
             global volumeRL
             global volumeCEN
             global volumeSW
             global volumeALLCH
	     if self.path.endswith(".ico"):
  	       return
	     query_components = parse_qs(urlparse(self.path).query)
             self.send_response(200)
             self.send_header('Content-type',	'text/html')
             self.end_headers()
             if query_components["task"][0] == "souce":
                 if query_components["value"][0] == "5.1":
		    writeLcdLine(SOUND_LCD,"Input 5.1",1)
                    bus.write_byte_data(PT2323_ADDRESS, DEVICE_REG_MODE1, 0xC7)
                 if query_components["value"][0] == "aux1":
		    writeLcdLine(SOUND_LCD,"Input RADIO",1)
                    bus.write_byte_data(PT2323_ADDRESS, DEVICE_REG_MODE1, 0xCB)
                 if query_components["value"][0] == "aux2":
		    writeLcdLine(SOUND_LCD,"Input AUX 2",1)
                    bus.write_byte_data(PT2323_ADDRESS, DEVICE_REG_MODE1, 0xCA)
                 if query_components["value"][0] == "aux3":
		    writeLcdLine(SOUND_LCD,"Input AUX 3",1)
                    bus.write_byte_data(PT2323_ADDRESS, DEVICE_REG_MODE1, 0xC9)
                 if query_components["value"][0] == "aux4":
		    writeLcdLine(SOUND_LCD,"Input AUX 4",1)
                    bus.write_byte_data(PT2323_ADDRESS, DEVICE_REG_MODE1, 0xC8)
		 self.wfile.write("ok")
	     if query_components["task"][0] == "enhanced":
                 if query_components["value"][0] == "on":
                    writeLcdLine(SOUND_LCD,"Enhanced ON",1)
                    bus.write_byte_data(PT2323_ADDRESS, DEVICE_REG_MODE1, 0xD0)
                 if query_components["value"][0] == "off":
                    writeLcdLine(SOUND_LCD,"Enhanced OFF",1)
                    bus.write_byte_data(PT2323_ADDRESS, DEVICE_REG_MODE1, 0xD1)
		 self.wfile.write("ok")
             if query_components["task"][0] == "mixchan":
                 if query_components["value"][0] == "on":
                    writeLcdLine(SOUND_LCD,"Mixed ON",1)
                    bus.write_byte_data(PT2323_ADDRESS, DEVICE_REG_MODE1, 0x90)
                 if query_components["value"][0] == "off":
                    writeLcdLine(SOUND_LCD,"Mixed OFF",1)
                    bus.write_byte_data(PT2323_ADDRESS, DEVICE_REG_MODE1, 0x91)
                 self.wfile.write("ok")

             if query_components["task"][0] == "mute":
		    writeLcdLine(SOUND_LCD,"Mute",1)
		    bus.write_byte_data(PT2323_ADDRESS, DEVICE_REG_MODE1, 0xFF)
                    self.wfile.write("ok")

             if query_components["task"][0] == "unmute":
		    writeLcdLine(SOUND_LCD,"Volume "+`volumeALLCH`+" dB",1)
                    bus.write_byte_data(PT2323_ADDRESS, DEVICE_REG_MODE1, 0xFE)
	            self.wfile.write("ok")
             if query_components["task"][0] == "volume":
		if query_components["type"][0] == "plus":
		    volumeALLCH = volumeALLCH + 1
                    writeLcdLine(SOUND_LCD,"Volume "+`volumeALLCH`+" dB",1)
                    pt2258(int(query_components["chanel"][0]) , 74-volumeALLCH)
		if query_components["type"][0] == "minus":
                    volumeALLCH = volumeALLCH - 1
                    writeLcdLine(SOUND_LCD,"Volume "+`volumeALLCH`+" dB",1)
		    pt2258(int(query_components["chanel"][0]), 74-volumeALLCH)
                if query_components["type"][0] == "chanel":
                    writeLcdLine(SOUND_LCD,"Volume "+query_components["chanel"][0]+": "+query_components["value"][0]+" dB",1)
                    self.wfile.write(pt2258(int(query_components["chanel"][0]), 74 - int(query_components["value"][0])))

             if query_components["task"][0] == "updatetime":
                    writeLcdLine(SOUND_LCD,strftime("%Y-%m-%d %H:%M", localtime()),2)
                    #writeLcdLine(BATHROOM_LCD,strftime("%H:%M", localtime()),1)
                    self.wfile.write("ok")
             if query_components["task"][0] == "writeline":
                    writeLcdLine(SOUND_LCD,query_components["text"][0],int(query_components["line"][0]))
                    self.wfile.write("ok")

	     if query_components["task"][0] == "ligth":
		if query_components["type"][0] == "toggle":
		    toggleLamp(int(query_components["lamp"][0]))
                if query_components["type"][0] == "on":
		    enableLamp(int(query_components["lamp"][0]))
                if query_components["type"][0] == "off":
		    disableLamp(int(query_components["lamp"][0]))
                if query_components["type"][0] == "state":
		    self.wfile.write(lampState())
                if query_components["type"][0] == "allon":
                    allOn()
                if query_components["type"][0] == "alloff":
                    allOff()
		    return 


def main():
    try:
        server = HTTPServer(('', 82), MyHandler)
        #server.bus = smbus.SMBus(1)
        print 'started httpserver...'
	bus.write_byte(PT2258_ADDRESS,0xC0);
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()



class MyDaemon(Daemon):
	        def run(self):
		        print 'started httpserver w...'
         	 	main()

if __name__ == '__madin__':
        main()

if __name__ == '__main__':
	#main()
	daemon = MyDaemon('/var/run/soundserver.pid')
        if len(sys.argv) == 2:
                if 'start' == sys.argv[1]:
                        writeLcdLine(SOUND_LCD,'start server    ',1)
                        #writeLcdLine(BATHROOM_LCD,'start server    ',1)
		        print 'started httpserver...'
                        daemon.start()
                elif 'stop' == sys.argv[1]:
                        writeLcdLine(SOUND_LCD,'stop server     ',1)
                        daemon.stop()
                elif 'restart' == sys.argv[1]:
                        writeLcdLine(SOUND_LCD,'restart server  ',1)
                        daemon.restart()
                else:
                        print "Unknown command"
                        sys.exit(2)
                sys.exit(0)
        else:
                print "usage: %s start|stop|restart" % sys.argv[0]
                sys.exit(2)


