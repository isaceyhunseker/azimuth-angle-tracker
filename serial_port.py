import serial, time
import serial.tools.list_ports
import pygatt
import pygatt.backends as pb
import pygatt.exceptions
import time
import tytserialport as tytserial
import datetime
import pandas
from datetime import datetime
from binascii import hexlify
from time import sleep
import os
import csv
#initialization and open the port

#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call

ser = serial.Serial()
#ser.port = "/dev/ttyUSB0"
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
ser.parity = serial.PARITY_NONE  # set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
#ser.timeout = None          #block read
#ser.timeout = 1            #non-block read
ser.timeout = 10              #timeout block read
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 10     #timeout for write

def findSerialPort():
    global ser
    comlist = serial.tools.list_ports.comports()
    #connected = []
    for element in comlist:
        # print(str(element.description))
        if element.description == "CP2102 USB to UART Bridge Controller" or "Silicon Labs CP210x USB to UART Bridge" in element.description:
            # print("Connecting to COM port: " + str(element.device))
            ser.port = element.device
            return True
    return False

def serialWrite(msg, expectedRspLen = 0):
    global ser
    if findSerialPort() != True:
        return False, "NO_PORT"
    
    try: 
        ser.open()
    except:
        # print("error opening serial port: " + str(e))
        sleep(2)
        ser.open()
  

    if ser.isOpen():
        try:
            ser.flushInput() #flush input buffer, discarding all its contents
            ser.flushOutput()#flush output buffer, aborting current output 
                    #and discard all that is in buffer

            #write data
            ser.write(bytearray(msg, 'ascii'))
            print("write data: {}".format(msg) )

            time.sleep(0.2)  #give the serial port some time to receive the data

            totalNumOfBytesFromSerial = 0
            numTrial = 0
            full_response = ""

            #while True:
            # response = ser.readline()
            # response = ser.readall()

            if expectedRspLen:
                response = ser.read(expectedRspLen - totalNumOfBytesFromSerial)
            else:
                response = ser.readall()

            totalNumOfBytesFromSerial += len(response)
            numTrial += 1

            full_response += response.hex()
            # full_response += response.decode("utf-8")

            print("expLen: " + str(expectedRspLen) + "  resLen: " + str(len(response)) + "  resDataHex: " + response.hex())

            ser.close()

            if totalNumOfBytesFromSerial == expectedRspLen:
                return True, full_response
            elif totalNumOfBytesFromSerial == 0:
                return False
            else:
                return False
            return False

        except:
            sleep(2)
            ser.write(bytearray(msg, 'ascii'))
            ser.close()
        finally:
            ser.close()

    else:
        return False


if __name__ == '__main__':
    pass
