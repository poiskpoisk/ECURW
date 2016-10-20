# -*- coding: utf-8 -*-
__author__ = 'АМА'

# Должен быть обязательно 64 bit Python, иначе windll даст ошибку !!!!!!!!!!

from PCANBasic import *  # PCAN-Basic library import
import time
import datetime
import os


from CRCModules.CRCCCITT import CRCCCITT

#---------------------Инициализация массивов ----------------------------------------------------
buf = [1, 2, 3, 4, 5, 6, 7, 8]
buf_all = [x  for x in range(3200) ]
s=''
# ----------------- Инициализируем канал связи с CAN -----------------------------------
myCAN = PCANBasic()
Init_result = myCAN.Initialize(PCAN_USBBUS1, PCAN_BAUD_125K)
if Init_result == PCAN_ERROR_OK:
    print 'Hardware successful init'
else:
    Err_decoding_result = myCAN.GetErrorText(Init_result, 9)
    if Err_decoding_result[0] != PCAN_ERROR_OK:
        print 'Error decoding initialize code error, return code:', hex(Init_result)
    else:
        print 'Init status: ', Err_decoding_result[1], ', return code:', hex(Init_result)
    raw_input()
# ---------------------- Получаем статус канала -------------------------------------------
Res_stat_result = myCAN.GetValue(PCAN_USBBUS1, PCAN_RECEIVE_STATUS)
if Res_stat_result[1] == 1:
    print 'Recive mode is ON, return code:', hex(Res_stat_result[1])
else:
    print 'Recive mode is OFF, return code:', hex(Res_stat_result[1])
# ------------------------------ Закрываем фильтр ----------------------------------------
strBuffer = PCAN_FILTER_CLOSE
Set_filter_result = myCAN.SetValue(PCAN_USBBUS1, PCAN_MESSAGE_FILTER, strBuffer)
if Set_filter_result == PCAN_ERROR_OK:
    print 'Filter is closed, return code:', hex(Set_filter_result)
else:
    print ' Error closing filter , return code:', hex(Set_filter_result)
# ------------------------------ Устанавливаем фильтр ----------------------------------------
FM_result = myCAN.FilterMessages(PCAN_USBBUS1, 0, 0x7FF, PCAN_MODE_STANDARD)
if FM_result == PCAN_ERROR_OK:
    print 'Filter is configured, return code:', hex(FM_result)
else:
    print ' Error configured filter , return code:', hex(FM_result)
#------------------------------Запись в буффер ХАНДШЕЙК------------------------------------------------------------
time.sleep(0.1)
rx_msg = TPCANMsg()
rx_msg.ID = 0x100
rx_msg.MSGTYPE = PCAN_MESSAGE_STANDARD
rx_msg.LEN = 8
rx_msg.DATA[0] = 8
rx_msg.DATA[1] = 7
rx_msg.DATA[2] = 6
rx_msg.DATA[3] = 5
rx_msg.DATA[4] = 4
rx_msg.DATA[5] = 3
rx_msg.DATA[6] = 2
rx_msg.DATA[7] = 1
write_result = myCAN.Write(PCAN_USBBUS1, rx_msg)
if write_result == PCAN_ERROR_OK:
    print 'Handshake written successful, return code:', hex(write_result)

else:
    print ' Handshake error , return code:', hex(write_result)
    raw_input()
    os._exit(2)

time.sleep(0.3)
#------------------------Открываем файл для хранения калибровки каждый раз новый по дате -----------------------------
now_time = datetime.datetime.now() # Текущая дата со временем
now_time=now_time.strftime(".\\data\\%d-%m-%y_%H-%M") +'.bin'
try:
    f = open(now_time, 'wb')
    print f
except:
    print ' File open error'
    raw_input()
    os._exit(5)
#------------------------------Чтение из буффера ------------------------------------------------------------

count_msg=0
CANMsg = TPCANMsg()  # We create a TPCANMsg message structure
Time_stamp = TPCANTimestamp()
readResult = PCAN_ERROR_OK,
print 'Reading from queue'
while (readResult[0] & PCAN_ERROR_QRCVEMPTY) != PCAN_ERROR_QRCVEMPTY:
    time.sleep(0.05)
    readResult = myCAN.Read(PCAN_USBBUS1)
    if readResult[0] == PCAN_ERROR_OK:
        count_msg+=1
        print 'Messages number:', count_msg, ' ID:', hex(readResult[1].ID), 'Type:', hex(
            readResult[1].MSGTYPE), 'Lenght:', hex(readResult[1].LEN), 'Time:', readResult[2].millis
        print 'DATA: ', hex(readResult[1].DATA[0]), hex(readResult[1].DATA[1]), hex(readResult[1].DATA[2]), hex(
            readResult[1].DATA[3]), hex(readResult[1].DATA[4]), hex(readResult[1].DATA[5]), hex(
            readResult[1].DATA[6]), hex(readResult[1].DATA[7])
        buf[0] = readResult[1].DATA[0]
        buf[1] = readResult[1].DATA[1]
        buf[2] = readResult[1].DATA[2]
        buf[3] = readResult[1].DATA[3]
        buf[4] = readResult[1].DATA[4]
        buf[5] = readResult[1].DATA[5]
        buf[6] = readResult[1].DATA[6]
        buf[7] = readResult[1].DATA[7]
        s = s+ chr(readResult[1].DATA[0])
        s = s+ chr(readResult[1].DATA[1])
        s = s+ chr(readResult[1].DATA[2])
        s = s+ chr(readResult[1].DATA[3])
        s = s+ chr(readResult[1].DATA[4])
        s = s+ chr(readResult[1].DATA[5])
        s = s+ chr(readResult[1].DATA[6])
        s = s+ chr(readResult[1].DATA[7])
    else:
        Err_decoding_result = myCAN.GetErrorText(readResult[0], 9)
        if Err_decoding_result[0] != PCAN_ERROR_OK:
            print 'Error decoding reading code error', ', return code:', hex(readResult[0])
        else:
            print 'Error reading from queue: ', Err_decoding_result[1], ', return code:', hex(readResult[0])
print 'Writing data', len(s), 'bytes'
f.write(s)
#--------------------Контроль CRC16 ---------------------------------------
print 'CRC checking'
s = s[:-2]
crc_calc  = CRCCCITT(version="1D0F").calculate(s)
crc_given = buf[7]*256+buf[6]
print 'CRC16 from ECU is ',crc_given,'calculated CRC16 is ',crc_calc
print 'High byte(*256) -',buf[7], 'Low byte - ', buf[6]
if crc_given == crc_calc :
    #------------------------Закрываем файл для хранения калибровки--------------------------------------
    print 'CRC16 is OK'
    print 'Closing data files'
    try:
        f.close()
        os._exit(10)
    except:
        print ' File closing error'
        raw_input()
        os._exit(6)
else:
    print 'CRC16 error !'
    raw_input()
    os._exit(9)


