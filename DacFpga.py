from serial import Serial
import sys
from time import *

#defines
enterLoadData = 1
enterLoadAdr = 2
enterAutoComp = 3
enterLoadMem = 4
enterNormMode = 5
enterLdHiData = 7
enterLdStatus = 8
enterLdDataCount = 9
enterLdDataSize = 10
enterLdOneRam = 11
enterRdRam = 13
enterRdDataCount = 17
enterLdClkDivider = 19

rst_in_n = 1 << 0;
en_in_n = 1 << 1;
external_clk_en = 1 << 2;
divider_clk_en = 1 << 3;

def loadAddresses( ser, data):
    global enterLdStatus
    global enterLoadAdr
    print "Loading addresses:" + repr(data)
    ser.write(chr(enterLdStatus))
    ser.write(chr(0))
    ser.write(chr(enterLoadAdr))
    ser.write(chr(0))
    ser.write(chr(enterLdStatus))
    ser.write(chr(rst_in_n))
    for i in range(144):
        ser.write(chr(enterLdStatus))
        ser.write(chr(en_in_n | rst_in_n))
        ser.write(chr(enterLoadAdr))
        ser.write(chr(data[i]))
        ser.write(chr(enterLdStatus))
        ser.write(chr(rst_in_n))
        ser.write(chr(enterLoadAdr))
        ser.write(chr(data[i]))
    ser.write(chr(enterLdStatus))
    ser.write(chr(en_in_n | rst_in_n))


print "Dac Fpga interface"
#TODO:ask for com port, later automate

comUse = raw_input("use com(y/n)?:") == "y"
if(comUse):
    ComString = raw_input("name com port:")
    ComNum = int(ComString)
    ser = Serial(ComNum - 1, 115200)
    #ser.write(chr(42))
    #if(ser.read() != chr(42)):
    #    print "Error connection bad"
    #    exit(1)
    ser.write(chr(enterLoadData))
    ser.write(chr(128))
    ser.write(chr(0))

dataSize = 1
#TODO: loop
while True:
    print """1)load data
2)load addresses
3)manual calibration
4)exit
5)load sequence
6)run sequence 100mhz
7)low frequency
8)load address (no reset)
9)reset addresses
10)simple manual calibration
11)run with options
"""
    Resp = int(raw_input("Choose 1,2,3,4,5,6,7,8,9,10,11:"))
    if Resp == 1: #Load data
        print "loading data"
        if(comUse):
            ser.write(chr(1))
        Resp = int(raw_input("Enter data value (0-32767):"))
        low = Resp % 256
        high = Resp / 256
        if(comUse):
            ser.write(chr(low))
            ser.write(chr(high))
    elif Resp == 2:
        print "loading addresses"
        print "enter 144 values (0-7) eg"
        print ">123456701234567012345670123456701234567012345670123456701234567012345670123456701234567012345670123456701234567012345670123456701234567012345670"
        Resp = raw_input(">")
        if(comUse):
            data = []
            for i in range(144):
                data.append(int(Resp[i]))
            loadAddresses(ser, data)
        
    elif Resp == 3:
        if(comUse):
            ser.write(chr(enterLoadData))
            ser.write(chr(128))
            ser.write(chr(0))
        #TODO: allow option to record from file
        differentials = range(144)
        evenOrOdd = range(144)
        for i in range(72):
            evenOrOdd[i] = 0
        for i in range(72, 144):
            evenOrOdd[i] = 1
        differentials[0] = 0
        evenOrOdd[0] = 1
        evenOrOdd[72] = 0
        if(comUse):
            print "entering round 1"
            for i in range(1,72):
                data = []
                for j in range(144):
                    if(i == j):
                        data.append(1)
                    elif(j == 0):
                        data.append(2)
                    elif(j < 73):
                        data.append(6)
                    else:
                        data.append(7)
                loadAddresses(ser, data)
                
                ser.write(chr(enterLdHiData))
                ser.write(chr(34)) #6 + 2
                raw_input("press Enter when calibrated")
                ser.write(chr(enterLdHiData))
                ser.write(chr(33)) #6 + 1
                Resp = float(raw_input("Enter deferential value:"))
                differentials[i] = Resp
            for i in range(72,144):
                data = []
                for j in range(144):
                    if(i == j):
                        data.append(1)
                    elif(j == 0):
                        data.append(2)
                    elif(j < 72):
                        data.append(6)
                    else:
                        data.append(7)
                loadAddresses(ser, data)
                        
                ser.write(chr(enterLdHiData))
                ser.write(chr(34))
                raw_input("press Enter when calibrated")
                ser.write(chr(enterLdHiData))
                ser.write(chr(33))
                Resp = float(raw_input("Enter deferential value:"))
                differentials[i] = Resp
        else:
            difFile = open('randomResp.txt', 'r')
            differentials = range(144)
            for i in range(144):
                differentials[i] = float(difFile.readline())
            difFile.close()

        sortedCurrentSources = sorted(range(144), key=lambda source: differentials[source])
        #discard 17
        for i in range(8):
            del sortedCurrentSources[0]
        for i in range(9):
            del sortedCurrentSources[127]

        currentSet0 = [sortedCurrentSources[63]]
        currentSets = range(8)
        currentSets[0] = currentSet0
        for i in range(63):
            sortedCurrentSources[i] = [[sortedCurrentSources[i],sortedCurrentSources[126 - i]],0]
        for i in range(64):
            del sortedCurrentSources[63]
        if(comUse):
            print "entering round 2"
            n = 2
            #use sortedCurrentSources[0] as reference
            for j in range(1,63):
                g1 = n
                g2 = n
                g6 = 72 - n
                g7 = 72 - n
                data = []
                for k in range(144):
                    if(k in sortedCurrentSources[j][0]):
                        data.append(1)
                        g1 = g1 - 1
                    elif(k in sortedCurrentSources[0][0]):
                        data.append(2)
                        g2 = g2 - 1
                    elif(g6 != 0):
                        g6 = g6 - 1
                        data.append(6)
                    else:
                        g7 = g7 - 1
                        data.append(7)
                loadAddresses(ser, data)
                        
                ser.write(chr(enterLdHiData))
                ser.write(chr(34)) #6 + 2
                raw_input("press Enter when calibrated")
                ser.write(chr(enterLdHiData))
                ser.write(chr(33)) #6 + 1
                Resp = float(raw_input("Enter deferential value:"))
                sortedCurrentSources[j][1] = Resp
        else:
            difFile = open('randomResp.txt', 'r')
            for i in range(63):
                sortedCurrentSources[i][1] = float(difFile.readline())
            difFile.close()
        sortedCurrentSources.sort(key=lambda curr: curr[1])
        currentSets[1] = sortedCurrentSources[63/2][0]
        numSets = 63
        for i in range(5):
            print "entering round " + repr(i + 3)
            currentSources = range(numSets/2)
            for j in range(numSets/2):
                currentSources[j] = [sortedCurrentSources[j][0] + sortedCurrentSources[numSets - j - 1][0],0]
            numSets = numSets / 2
            if(comUse):
                n = n * 2
                for k in range(1, numSets):
                    g1 = n
                    g2 = n
                    g6 = 72 - n
                    g7 = 72 - n
                    data = []
                    for l in range(144):
                        if(l in currentSources[k][0]):
                            data.append(1)
                            g1 = g1 - 1
                        elif(l in currentSources[0][0]):
                            data.append(2)
                            g2 = g2 - 1
                        elif(g6 != 0):
                            data.append(6)
                            g6 = g6 - 1
                        else:
                            data.append(7)
                            g7 = g7 - 1
                    loadAddresses(ser, data)
            
                    ser.write(chr(enterLdHiData))
                    ser.write(chr(34))
                    raw_input("pressEnter when calibrated")
                    ser.write(chr(enterLdHiData))
                    ser.write(chr(33))
                    Resp = float(raw_input("Enter deferential value:"))
                    currentSources[k][1] = Resp
            else:
                difFile = open('randomResp.txt', 'r')
                for j in range(numSets):
                    currentSources[j][1] = float(difFile.readline())
                difFile.close()
            sortedCurrentSources = sorted(currentSources, key=lambda curr: curr[1])
            currentSets[i + 2] = sortedCurrentSources[numSets/2][0]
        strOut = ""
        for i in range(144):
            check = 0
            for j in range(7):
                if i in currentSets[j]:
                    strOut = strOut + repr(j + 1)
                    if check == 1:
                        print "error at:" + repr(i) + " and " + repr(j)
                    check = 1
            if check == 0:
                strOut = strOut + repr(0)
        print strOut
        
    elif Resp == 5:
        f = open('sequence.csv')
        vals = f.read().split(",")
        data = []
        for i in range(len(vals)):
            if vals[i] == '':
                continue
            data.append(int(vals[i]))
        f.close()
        dataSize = len(data) - 1
        print "data length:" + repr(len(data))
        if(len(data) > 72000):
            print "WARNING: Loading more data than available in fpga, undefined behavior."
        #send data to fpga
        if(comUse):
            for i in range(len(data)):
                ser.write(chr(enterLdDataCount))
                ser.write(chr(i % 256))
                ser.write(chr(i / 256 % 256))
                ser.write(chr(i / 256 / 256 % 256))
                ser.write(chr(i / 256 / 256 / 256 % 256))
                ser.write(chr(enterLdOneRam))
                ser.write(chr(data[i] % 256))
                ser.write(chr(data[i] / 256))
                
    elif Resp == 6:
        if(comUse):
            ser.write(chr(enterLdDataCount))
            ser.write(chr(0))
            ser.write(chr(0))
            ser.write(chr(0))
            ser.write(chr(0))
            ser.write(chr(enterLdDataSize))
            ser.write(chr(dataSize % 256))
            ser.write(chr(dataSize / 256 % 256))
            ser.write(chr(dataSize / 256 / 256 % 256))
            ser.write(chr(dataSize / 256 / 256 / 256 % 256))
            ser.write(chr(enterNormMode))
            Resp = raw_input("press enter to end")
            ser.write(chr(0))
    elif Resp == 7:
        Resp = float(raw_input("enter period in seconds (min .003):"))
        period = Resp - .003
        if(period < 0):
            period = 0
        f = open('sequence.csv', 'r')
        vals = f.read().split(",")
        for i in range(len(vals)):
            vals[i] = int(vals[i])
        print "loading values:" + repr(vals)
        if(comUse):
            for i in range(len(vals)):
                val = vals[i]
                ser.write(chr(enterLoadData))
                ser.write(chr(val%256))
                ser.write(chr(val/256))
                sleep(period)
        f.close()
    elif Resp == 8:
        if(comUse):
            ser.write(chr(enterLdStatus))
            ser.write(chr(rst_in_n))
            ser.write(chr(enterLoadAdr))
            Resp = int(raw_input("enter addess 0-7:"))
            ser.write(chr(Resp))
            ser.write(chr(enterLdStatus))
            ser.write(chr(en_in_n | rst_in_n))
    elif Resp == 9:
        if(comUse):
            ser.write(chr(enterLdStatus))
            ser.write(chr(0))
            ser.write(chr(enterLoadAdr))
            ser.write(chr(0))
            ser.write(chr(enterLdStatus))
            ser.write(chr(en_in_n | rst_in_n))
            
    elif Resp == 10:
        print "simple manual sort"
        if(comUse):
            ser.write(chr(enterLoadData))
            ser.write(chr(128))
            ser.write(chr(0))
        timeDelay = int(raw_input("enter time delay in seconds:"))
        #TODO: allow option to record from file
        differentials = range(144)
        evenOrOdd = range(144)
        for i in range(72):
            evenOrOdd[i] = 0
        for i in range(72, 144):
            evenOrOdd[i] = 1
        differentials[0] = 0
        evenOrOdd[0] = 1
        evenOrOdd[72] = 0
        if(comUse):
            for i in range(1,73):
                data = []
                for j in range(144):
                    if(i == j):
                        data.append(1)
                    elif(j == 0):
                        data.append(2)
                    elif(j < 73):
                        data.append(6)
                    else:
                        data.append(7)
                loadAddresses(ser, data)
                if(i == 1):
                    ser.write(chr(enterLdHiData))
                    ser.write(chr(33)) #6 + 1
                    print "data:010000110000000"
                    print "calibrate now\a\a"
                    sleep(timeDelay)
                ser.write(chr(enterLdHiData))
                ser.write(chr(34)) #6 + 2
                print "data:010001010000000"
                print "Record value " + repr(i + 1) + "now\a"
                sleep(timeDelay)
                #Resp = float(raw_input("Enter deferential value:"))
                #differentials[i] = Resp
            
            ser.write(chr(enterLdHiData))
            ser.write(chr(33))
            print "data:010000110000000"
            print "check calibration\a\a"
            sleep(timeDelay)
            for i in range(73,144):
                data = []
                for j in range(144):
                    if(i == j):
                        data.append(1)
                    elif(j == 0):
                        data.append(2)
                    elif(j < 72):
                        data.append(6)
                    else:
                        data.append(7)
                loadAddresses(ser, data)
                if(i == 73):
                    ser.write(chr(enterLdHiData))
                    ser.write(chr(65))
                    print "data:100000110000000"
                    print "calibrate now\a\a"
                    sleep(timeDelay)
                    
                ser.write(chr(enterLdHiData))
                ser.write(chr(66))
                print "data:100001010000000"
                print "Record value " + repr(i + 1) + "now\a"
                sleep(timeDelay)
                #Resp = float(raw_input("Enter deferential value:"))
                #differentials[i] = Resp
        else:
            difFile = open('randomResp.txt', 'r')
            differentials = range(144)
            for i in range(144):
                differentials[i] = float(difFile.readline())
            difFile.close()
        if(comUse):
            print "data:100000110000000"
            print "check calibration\a\a"
            ser.write(chr(enterLdHiData))
            ser.write(chr(65))
            sleep(timeDelay)
        print "calibration finished"
        Resp = raw_input("would you like to continue(y/n)?")
        if(Resp == "n"):
            continue
        Resp = raw_input("Enter 143 values seperated by commas (eg 1,2,42,...):")
        differentials[0] = 0
        vals = Resp.split(",")
        print "the values for each current source are:" + repr(differentials)
        for i in range(1,144):
            differentials[i] = int(vals[i - 1])
        sortedCurrentSources = sorted(range(144), key=lambda source: differentials[source])
        #discard 17
        for i in range(8):
            del sortedCurrentSources[0]
        for i in range(9):
            del sortedCurrentSources[127]

        currentSet0 = [sortedCurrentSources[63]]
        currentSets = range(8)
        currentSets[0] = currentSet0
        for i in range(63):
            sortedCurrentSources[i] = [[sortedCurrentSources[i],sortedCurrentSources[126 - i]],differentials[sortedCurrentSources[i]] + differentials[sortedCurrentSources[126 - i]]]
        for i in range(64):
            del sortedCurrentSources[63]

        sortedCurrentSources.sort(key=lambda curr: curr[1])
        currentSets[1] = sortedCurrentSources[63/2][0]
        numSets = 63
        for i in range(5):
            currentSources = range(numSets/2)
            for j in range(numSets/2):
                currentSources[j] = [sortedCurrentSources[j][0] + sortedCurrentSources[numSets - j - 1][0],sortedCurrentSources[j][1] + sortedCurrentSources[numSets - j - 1][1]]
            numSets = numSets / 2
            sortedCurrentSources = sorted(currentSources, key=lambda curr: curr[1])
            currentSets[i + 2] = sortedCurrentSources[numSets/2][0]
        strOut = ""
        for i in range(144):
            check = 0
            for j in range(7):
                if i in currentSets[j]:
                    strOut = strOut + repr(j + 1)
                    if check == 1:
                        print "error at:" + repr(i) + " and " + repr(j)
                    check = 1
            if check == 0:
                strOut = strOut + repr(0)
        print strOut
    elif Resp == 11:
        if(comUse):
            ser.write(chr(enterLdDataCount))
            ser.write(chr(0))
            ser.write(chr(0))
            ser.write(chr(0))
            ser.write(chr(0))
            
            ser.write(chr(enterLdDataSize))
            ser.write(chr(dataSize % 256))
            ser.write(chr(dataSize / 256 % 256))
            ser.write(chr(dataSize / 256 / 256 % 256))
            ser.write(chr(dataSize / 256 / 256 / 256 % 256))
            Resp = int(raw_input("Choose clk 100mhz(1), divided clk(2), external clk(3):"))
            if(Resp == 1):
                ser.write(chr(enterLdStatus))
                ser.write(chr(en_in_n | rst_in_n))
            if(Resp == 2):
                Resp = int(raw_input("Enter desired frequency in hertz:"))
                #new frequency = 100Mhz / 2 / divider
                divider = int((100000000 / (2 * (Resp * 1.0 + .1))))
                if(divider < 0):
                    divider = 0
                if(divider >= 2**32):
                    print "cant load divider"
                    continue
                ser.write(chr(enterLdStatus))
                ser.write(chr(divider_clk_en | en_in_n | rst_in_n))
                ser.write(chr(enterLdClkDivider))
                ser.write(chr(divider % 256))
                ser.write(chr((divider / 256) % 256))
                ser.write(chr((divider / (256**2)) % 256))
                ser.write(chr((divider / (256**3)) % 256))
            if(Resp == 3):
                ser.write(chr(enterLdStatus))
                ser.write(chr(external_clk_en | en_in_n | rst_in_n))
            
            ser.write(chr(enterNormMode))
            Resp = raw_input("press enter to end")
            ser.write(chr(0))
            ser.write(chr(enterLdStatus))
            ser.write(chr(en_in_n | rst_in_n))
    elif Resp == 12:
        print """Broken
1)load word to ram
2)set count
3)set size
4)read ram to output
5)run high speed
6)set clock
7)read data count"""
        Resp = int(raw_input("choice:"))
        if Resp == 1:
            Resp = int(raw_input("enter data"))
            ser.write(chr(enterLdOneRam))
            ser.write(chr(Resp % 256))
            ser.write(chr(Resp / 256))
            pass
        elif Resp == 2:
            Resp = int(raw_input("set counter:"))
            ser.write(chr(enterLdDataCount))
            ser.write(chr(Resp % 256))
            ser.write(chr(Resp / 256))
            pass
        elif Resp == 3:
            Resp = int(raw_input("set size:"))
            ser.write(chr(enterLdDataSize))
            ser.write(chr(Resp % 256))
            ser.write(chr(Resp / 256))
            pass
        elif Resp == 4:
            ser.write(chr(enterRdRam))
            pass
        elif Resp == 5:
            for i in range(100):
                ser.write(chr(enterLdDataCount))
                ser.write(chr(i))
                ser.write(chr(0))
                ser.write(chr(enterLdOneRam))
                ser.write(chr(0))
                ser.write(chr(0))
            for i in range(100,200):
                ser.write(chr(enterLdDataCount))
                ser.write(chr(i))
                ser.write(chr(0))
                ser.write(chr(enterLdOneRam))
                ser.write(chr(1))
                ser.write(chr(0))
            ser.write(chr(enterLdDataCount))
            ser.write(chr(0))
            ser.write(chr(0))
            ser.write(chr(enterLdDataSize))
            ser.write(chr(200))
            ser.write(chr(0))
            ser.write(chr(enterNormMode))
            pass
        elif Resp == 6:
            Resp = int(raw_input("Enter desired frequency in hertz:"))
            #new frequency = 100Mhz / 2 / divider
            divider = int((100000000 / (2 * ((Resp + 1) * 1.0))) - 1)
            if(divider < 0):
                divider = 0
            if(divider >= 2**32):
                print "cant load divider"
                continue
            ser.write(chr(enterLdStatus))
            ser.write(chr(divider_clk_en | en_in_n | rst_in_n))
            ser.write(chr(enterLdClkDivider))
            ser.write(chr(divider % 256))
            ser.write(chr((divider / 256) % 256))
            ser.write(chr((divider / (256**2)) % 256))
            ser.write(chr((divider / (256**3)) % 256))

            ser.write(chr(enterNormMode))
            Resp = raw_input("press enter to end")
            ser.write(chr(0))
            ser.write(chr(enterLdStatus))
            ser.write(chr(en_in_n | rst_in_n))
            
        elif Resp == 7:
            ser.write(chr(enterRdDataCount))
            print "s0"
            returnData = ser.read(size=1)

            print "count:" + repr(returnData)
        #TODO: add read register commands
        else:
            pass
        
        
    else:
        break
