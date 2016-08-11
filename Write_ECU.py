# -*- coding: utf-8 -*-
__author__ = 'АМА'

# Должен быть обязательео 64 bit Python иначе windll даст ошибку !!!!!!!!!!

from PCANBasic import *  # PCAN-Basic library import
import time
import os
import pickle
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
    os._exit(1)
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
time.sleep(0.05)
rx_msg = TPCANMsg()
rx_msg.ID = 0x100
rx_msg.MSGTYPE = PCAN_MESSAGE_STANDARD
rx_msg.LEN = 8
rx_msg.DATA[0] = 1
rx_msg.DATA[1] = 2
rx_msg.DATA[2] = 3
rx_msg.DATA[3] = 4
rx_msg.DATA[4] = 5
rx_msg.DATA[5] = 6
rx_msg.DATA[6] = 7
rx_msg.DATA[7] = 8
write_result = myCAN.Write(PCAN_USBBUS1, rx_msg)
if write_result == PCAN_ERROR_OK:
    print 'Handshake written successful, return code:', hex(write_result)
else:
    print ' Handshake error , return code:', hex(write_result)
    raw_input()


    os._exit(2)
#------------------------Открываем файл калибровки -----------------------------
with open('.\\data\\ecu.bin', 'rb') as f:
    print f
    print 'Reading data file'
    cal_data = f.read()
    print 'Read', len(cal_data), 'bytes'
#---------------------- Закрываем файл --------------------------------------
print 'Closing data files'
try:
    f.close()
except:
    print ' File closing error'
    raw_input()
    os._exit(7)
#------------------------------Запись в буффер ------------------------------------------------------------
count_msg=0
print 'Writing to queue', len(cal_data), 'bytes'
while count_msg<>len(cal_data):
    rx_msg.ID = 0x100
    rx_msg.MSGTYPE = PCAN_MESSAGE_STANDARD
    rx_msg.LEN = 8
    rx_msg.DATA[0] = ord(cal_data[count_msg])
    rx_msg.DATA[1] = ord(cal_data[count_msg+1])
    rx_msg.DATA[2] = ord(cal_data[count_msg+2])
    rx_msg.DATA[3] = ord(cal_data[count_msg+3])
    rx_msg.DATA[4] = ord(cal_data[count_msg+4])
    rx_msg.DATA[5] = ord(cal_data[count_msg+5])
    rx_msg.DATA[6] = ord(cal_data[count_msg+6])
    rx_msg.DATA[7] = ord(cal_data[count_msg+7])
    time.sleep(0.05)
    write_result = myCAN.Write(PCAN_USBBUS1, rx_msg)
    if write_result == PCAN_ERROR_OK:
        print 'Messages number:',count_msg, 'Msg:',rx_msg.DATA[0],rx_msg.DATA[1],rx_msg.DATA[2],rx_msg.DATA[3],rx_msg.DATA[5],rx_msg.DATA[5],rx_msg.DATA[6],rx_msg.DATA[7]
        count_msg+=8
    else:
        Err_decoding_result = myCAN.GetErrorText(write_result, 9)
        if Err_decoding_result[0] != PCAN_ERROR_OK:
            print 'Error decoding writing code error', ', return code:', hex(write_result)
        else:
            print 'Error writing to queue: ', Err_decoding_result[1], ', return code:', hex(write_result)
        raw_input()
        os._exit(6)

#--------------------Контроль CRC16 ---------------------------------------
print 'CRC checking'
CANMsg = TPCANMsg()  # We create a TPCANMsg message structure
Time_stamp = TPCANTimestamp()
readResult = PCAN_ERROR_OK,
print 'Reading from queue'
while True:
    time.sleep(0.05)
    readResult = myCAN.Read(PCAN_USBBUS1)
    if readResult[0] == PCAN_ERROR_OK:
        print 'CRC confirm is ',readResult[1].DATA[0],readResult[1].DATA[1],readResult[1].DATA[2],readResult[1].DATA[3],readResult[1].DATA[4],readResult[1].DATA[5],readResult[1].DATA[6],readResult[1].DATA[7]
        if (readResult[0] == PCAN_ERROR_OK and readResult[1].DATA[0] == 1 and readResult[1].DATA[1] == 9 and
        readResult[1].DATA[2] == 7 and readResult[1].DATA[3] == 2 and readResult[1].DATA[4] == 1 and
        readResult[1].DATA[5] == 9 and readResult[1].DATA[6] == 7 and readResult[1].DATA[7] == 2 ):
            print 'ECU writing.'
            exit(0)
        else:
            print 'CRC16 error. ECU don''t write'
            raw_input()
            exit(50)
    else:
            print 'Not reading'

