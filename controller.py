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
fakecounter = 0

Imported_Data = pandas.read_csv\
    ("azimuth_angle_onlyangle.csv", sep=',', low_memory=False,
     names=[ 'AngleOfSun'])

currentDateTime = datetime.now()
minuteOfDay = int(currentDateTime.strftime("%H")) * 60 + int(currentDateTime.strftime("%M"))
lastOperationForNewDayOp = minuteOfDay +fakecounter
lastOperationForDoubleRoutineOp = minuteOfDay+fakecounter
minuteOfDayLastRoutineOperation = minuteOfDay+fakecounter

countForPositiveError = 0
countForNegativeError = 0
BothMotorsAvailables = 0


motorControlCharacteristicUUID = '7cb459c9-8d24-428e-b988-e05209c74b64'
motorControlCharacteristicStatusUUID = '3e60e9c9-7372-40d6-80a2-de2405b7dc95'
AzimuthAngleCharacteristicUUID = '9ad44c44-9cf8-4d7d-8418-f029f7455428'
RemoteMotor_MAC = '3C:71:BF:FE:6A:CE'
AzimutSensor_MAC = '3C:71:BF:FE:4D:3A'
# MainMotor_MAC = '3C:71:BF:FE:71:D6'

checkAvailibityOfESP32Cmd = '1'
correctionOperationCmd = '2'
correctionOperationReverseCmd = '3'
routineOperationCmd = '4'
newDayPositionOperationCmd = '5'
acknowledgeTrue = 6

ble_adapter = pb.GATTToolBackend()


def checkAvailablityOfMotors(retriesForMotor = 0, retriesForMotor_RW = 0, retriesForMainMotor = 0):
    global BothMotorsAvailable
    print("checkAvailablityOfMotorsFuncStarted")
    ble_adapter.start()
    sleep(2)
    if (retriesForMotor > 20) or (retriesForMotor_RW > 20) or (retriesForMainMotor > 2):
        print ("reboot coming!")
        sleep(30)
        os.system('sudo reboot')
        return False
    try:
        Motor = ble_adapter.connect(RemoteMotor_MAC)
        sleep(1)
        print("RemoteMotorConnected")
        try:
            acknowledge = Motor.char_read(motorControlCharacteristicStatusUUID)
            sleep(1)
            print(acknowledge, acknowledgeTrue)
            if (int(acknowledge)) == acknowledgeTrue:
                print("RemoteMotorACKTrue")
                ble_adapter.stop()
                res = tytserial.serialWrite(checkAvailibityOfESP32Cmd, 1)
                if res[0]:
                    serialvalue = int(res[1]) - 30
                    if serialvalue == acknowledgeTrue:
                        print("BothMotorsAvailable!")
                        BothMotorsAvailable = 1
                    else:
                        print("TheValueAckFromMainMotorWrong")
                        #return False
                else:
                    retriesForMainMotor += 1
                    print("MainMotorDidnotConnected")
                    retriesForMainMotor+=1
                    checkAvailablityOfMotors(retriesForMainMotor)
                    #return False
            else:
                ble_adapter.stop()
                print("TheValueAckFromRemoteMotorWrong")
                #return False
        except (pygatt.exceptions.NotConnectedError, pygatt.exceptions.NotificationTimeout, pygatt.exceptions.BLEError):
            retriesForMotor_RW += 1
            print("didnotreadfromremotemotor")
            sleep(0.5)
            ble_adapter.stop()
            sleep(0.5)
            checkAvailablityOfMotors(retriesForMotor_RW)
        finally:
            ble_adapter.stop()   
    except (pygatt.exceptions.NotConnectedError, pygatt.exceptions.NotificationTimeout, pygatt.exceptions.BLEError):
        retriesForMotor += 1
        print("ble_adapterdidnotconnectedtoremotemotor")
        sleep(0.5)
        ble_adapter.stop()
        sleep(0.5)
        checkAvailablityOfMotors(retriesForMotor)
        #return False
    finally:
        ble_adapter.stop()    


def Operation(OperationCmd,retriesForMotor=0, retriesForMotor_RW=0):
    motorOpStatus = '0'
    print("checkAvailablityOfMotors() is True_OperationStarted", OperationCmd)
    ble_adapter.start()
    sleep(2)
    if (retriesForMotor > 15) or (retriesForMotor_RW > 15):
        return False
    try:
        Motor = ble_adapter.connect(RemoteMotor_MAC)
        sleep(1)
        print("RemoteMotorConnectedinOperation")
        try:
            Motor.char_write(motorControlCharacteristicUUID, bytearray(OperationCmd, 'ascii'), wait_for_response=True)
            tytserial.serialWrite(OperationCmd, 1)
            sleep(0.7)
            print("commandSent: {}".format(OperationCmd))
            ble_adapter.stop()
            countForPositiveError = 0
            countForNegativeError = 0
            minuteOfDayLastRoutineOperation = minuteOfDay
            try:
                csvfile = open('/mnt/wb1datas/wbdatas.csv', 'a')
                writer = csv.writer(csvfile)
                writer.writerow([datetime.now()])
                print("writer.writerow([minuteOfDay])")
                csvfile.close()
            except:
                print("failonusb")
            print("opsuccess")

        except (pygatt.exceptions.NotConnectedError, pygatt.exceptions.NotificationTimeout, pygatt.exceptions.BLEError):
            retriesForMotor_RW += 1
            print("didnotRWvalue", RemoteMotor_MAC)
            sleep(0.5)
            ble_adapter.stop()
            sleep(0.5)
            Operation(OperationCmd, retriesForMotor_RW)
        finally:
            sleep(0.5)
            ble_adapter.stop()
    
    except (pygatt.exceptions.NotConnectedError, pygatt.exceptions.NotificationTimeout, pygatt.exceptions.BLEError):
        retriesForMotor+=1
        print("didnotconnectedtomotor", RemoteMotor_MAC)
        sleep(0.5)
        ble_adapter.stop()
        sleep(0.5)
        Operation(OperationCmd, retriesForMotor)
    finally:
        sleep(0.5)
        ble_adapter.stop()


def checkAzimuthAngle():
    print("checkAzimuthAngle()")
    ble_adapter.start()
    sleep(1)
    try:
        AzimutSensor = ble_adapter.connect(AzimutSensor_MAC)
        print(" AzimutSensor = ble_adapter.connect(AzimutSensor_MAC)")
        sleep(1)
        try:
            CurrentAzimuthAngle = AzimutSensor.char_read(AzimuthAngleCharacteristicUUID)[0]
            CurrentAzimuthAngle = (int(CurrentAzimuthAngle)*2)-180
            CurrentAzimuthAngle = -45+(abs(-45-CurrentAzimuthAngle)*1.9)
            ble_adapter.stop()
            sleep(1)
            return int(CurrentAzimuthAngle)
        except (pygatt.exceptions.NotConnectedError, pygatt.exceptions.NotificationTimeout):
            print("connected but didnot read from azimuthAngle")
            ble_adapter.stop()
            return -200
        finally:
            sleep(0.5)
            ble_adapter.stop()
    except (pygatt.exceptions.NotConnectedError, pygatt.exceptions.NotificationTimeout):
        print("noconnecttoazimuthsensor")
        sleep(0.5)
        ble_adapter.stop()
        return -200
    finally:
        sleep(0.5)
        ble_adapter.stop()    


def checkDislocation(azimuthAngle):
    if azimuthAngle > -190:
        AngleOfSun = Imported_Data['AngleOfSun'][minuteOfDay + 1 + fakecounter]
        magnitudeOfError = azimuthAngle - AngleOfSun  
        print(azimuthAngle,AngleOfSun,"azimuthAngle - AngleOfSun")
        if magnitudeOfError > 8:
          global countForPositiveError
          countForPositiveError +=1
          if countForPositiveError > 15:
              CheckDevicesAndOperate(correctionOperationCmd)
              countForPositiveError = 0
        elif magnitudeOfError < -8:
          global countForNegativeError
          countForNegativeError +=1
          if countForNegativeError > 15:
              CheckDevicesAndOperate(correctionOperationReverseCmd)
              countForNegativeError = 0
        else:
            countForPositiveError = 0
            countForNegativeError = 0
        print(countForPositiveError,countForNegativeError,"counters")    

def CheckDevicesAndOperate(OperationCmd):
    global BothMotorsAvailable
    print("OperationStarted", OperationCmd)
    checkAvailablityOfMotors()
    if BothMotorsAvailable is 1:
        print(BothMotorsAvailable,"result is")
        Operation(OperationCmd)
        BothMotorsAvailable = 0    



def main():
    sleep(5)
    global currentDateTime, minuteOfDay, lastOperationForNewDayOp, lastOperationForDoubleRoutineOp, minuteOfDayLastRoutineOperation
    minuteOfDay = int(datetime.now().strftime("%H")) * 60 + int(datetime.now().strftime("%M"))+fakecounter
  
    print(minuteOfDay,minuteOfDayLastRoutineOperation)
    if (830 > minuteOfDay > 590) and (minuteOfDay - minuteOfDayLastRoutineOperation >= 28):
        print ("reboot coming no action last 28 minute!")
        sleep(30)
        os.system('sudo reboot')    
    if (830 > minuteOfDay > 590) and (minuteOfDay - minuteOfDayLastRoutineOperation >= 13):
        CheckDevicesAndOperate(routineOperationCmd)
    if ((740 >= minuteOfDay >= 737) or (784 >= minuteOfDay >= 782)) and (minuteOfDay - lastOperationForDoubleRoutineOp >= 30):
        lastOperationForDoubleRoutineOp = minuteOfDay
        CheckDevicesAndOperate(routineOperationCmd)
    if (988 >= minuteOfDay >= 985) and (minuteOfDay - lastOperationForNewDayOp >= 300):
        lastOperationForNewDayOp = minuteOfDay
        CheckDevicesAndOperate(newDayPositionOperationCmd)
    if 580 >= minuteOfDay >= 590:
        lastOperationForDoubleRoutineOp = minuteOfDay
        lastOperationForNewDayOp = minuteOfDay

    checkDislocation(checkAzimuthAngle())    


if __name__ == '__main__':
    sleep(5)
    while True:
        main()

