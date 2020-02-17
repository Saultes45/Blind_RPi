#!/usr/bin/env python
# -*- coding: utf-8 -*-   

# -------------------Metadata----------------------
# Creator: Nathanael ESNAULT

# nathanael.esnault@gmail.com
# or
# nesn277@aucklanduni.ac.nz

# Creation date 01/02/2019 (Waitangi day--> SUPER important)
# Version	0.1

# Github: 
# BitBucket: 

# TODO list: 
# 


# -------------------VERY important notes----------------------
#sudo pip install pexpect
#sudo gatttool -i hci0 -t random -b F7:E1:D3:98:47:9E --sec-level=high --char-write -u 0x0025 -n 45

# -------------------Import modules----------------------------


from time import sleep
from time import time

import subprocess
import os 

import sys
from subprocess import PIPE, Popen
from threading  import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x
import pexpect    

# ------------------- def ----------------------------

def PreapareBLE(verbose):
    errorOccured = 0
    try:
        print 'Preaparing BLE...'

        print "--> Restarting BLE"
        subprocess.call('sudo service bluetooth restart'.split(" ")) #no output
        print "--> Done"

        stdOutValue = subprocess.check_output('hciconfig')
        if verbose:
            print "\n\n\n"
            print stdOutValue
        # you can split by any value, here is by space
        my_output_list = stdOutValue.split(" ")
        if (("UP" in my_output_list[14]) and ("RUNNING" in my_output_list[15])):
            print "The BLE is already up and running"

        
        subprocess.call('sudo hciconfig hci0 up'.split(" ")) #no output
        stdOutValue = subprocess.check_output('hciconfig')
        
        if verbose:
            print "\n\n\n"
            print stdOutValue
        # you can split by any value, here is by space
        my_output_list = stdOutValue.split(" ")
        if (("UP" in my_output_list[14]) and ("RUNNING" in my_output_list[15])):
            print "The BLE is up and running"
        else:
            "Error: BLE still down"
            errorOccured = 1

    except Exception:
        print 'Error while preaparing BLE'
        errorOccured = 1

    return errorOccured    


def ShutdownBLE(verbose):
    errorOccured = 0
    print 'Shutting down BLE...'
    try:
        
        stdOutValue = subprocess.check_output('hciconfig')
        if verbose:
            print "\n\n\n"
            print stdOutValue
        # you can split by any value, here is by space
        my_output_list = stdOutValue.split(" ")
        if (("UP" in my_output_list[14]) and ("RUNNING" in my_output_list[15])):
            print "The BLE was up and running"

        
        subprocess.call('sudo hciconfig hci0 down'.split(" ")) #no output

        stdOutValue = subprocess.check_output('hciconfig')
        if verbose:
            print "\n\n\n"
            print stdOutValue
        # you can split by any value, here is by space
        my_output_list = stdOutValue.split(" ")
        if ("DOWN" in my_output_list[14]):
            print '--> BLE is down'        
        
        print 'All done'

    except Exception:
        print 'Error while shutting down BLE'
        errorOccured = 1

    return errorOccured   

def enqueue_output(out, queue):
    try:
        for line in iter(out.readline, b''):
            queue.put(line)
            out.close()
    except IOError as e:
        pass


# ------------------- BLE ----------------------------
# Configure the BLE
if __name__ == '__main__':

    BusyError = "Error: connect: Device or resource busy"
    ON_POSIX = 'posix' in sys.builtin_module_names 

    PreapareBLE(0)

    p = Popen('sudo timeout -s SIGINT 5s hcitool -i hci0 lescan'.split(" "), bufsize=1, close_fds=ON_POSIX, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    # stdout = normal output
    # stderr = error output
    if  stderr != '':
        print "Error while scanning: " + stderr
    else:
        #print stdout

        my_output_list = stdout.split("\n")

        MaxNumberOfSensors = 1
        SensorTagFoundList = ['0:0'] * MaxNumberOfSensors

        nbrSensorTagFound = 0 #init
        #nbrTagFound=0#init
        for line in my_output_list:
            #print line
            if "Adafruit Bluefruit LE" in line:
                nbrSensorTagFound += 1
                sensortag = line[:line.rfind(" ")]
                 # remove the name of the device and get only the MAC adddrrss
                while sensortag.rfind(" ") != -1:
                    sensortag = sensortag[:sensortag.rfind(" ")]
                SensorTagFoundList[nbrSensorTagFound-1] = sensortag
                print str(nbrSensorTagFound) + " SensorTag found: " + sensortag




        # Run gatttool non-interactively.
        print("Starting gatttool...")

        child = []
        for cnt_DetectedSensors in range(0, nbrSensorTagFound):
            Mycommand = 'sudo gatttool -i hci0 -t random -b ' + SensorTagFoundList[cnt_DetectedSensors] + ' --sec-level=high -I'
            #Mycommand = 'sudo gatttool -i hci0 -t random -b ' + SensorTagFoundList[cnt_DetectedSensors]  + ' --sec-level=high'
            child.append(pexpect.spawn(Mycommand))
            print 'Sending: ' + Mycommand
            sleep(5)

            # Connect to the device.
            returnCode = child[cnt_DetectedSensors].sendline("connect")
            rIndex = child[cnt_DetectedSensors].expect(["Connection successful", BusyError, pexpect.EOF, pexpect.TIMEOUT], timeout=10)
            if returnCode == 8 and rIndex == 0:
                print "Command successful"
                print("Connected to arm device!")
            elif returnCode == 9:
                print "Command failed"
            else:
                print "Command Unknown"


            #send the "I am now connected?" transaction

            child[cnt_DetectedSensors].sendline("char-write-cmd 0x0025 470A") # we don't have feedback (yet, maybe an echo sometime) 0x47 (ASCII) 0x0A (ASCII '\n')

            returnCode = child[cnt_DetectedSensors].sendline("disconnect")
#            rIndex = child[cnt_DetectedSensors].expect(["GLib-WARNING ", BusyError, pexpect.EOF, pexpect.TIMEOUT], timeout=10)
            rIndex = child[cnt_DetectedSensors].expect(["gatttool:", BusyError, pexpect.EOF, pexpect.TIMEOUT], timeout=10)
            
            if returnCode == 11 and rIndex == 0:
                print "Command successful"
            else:
                print "Disconnect unsuccessful :("


    ShutdownBLE(0)



