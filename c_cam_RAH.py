#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python3
import time
from pyfirmata import Arduino, util
import tornado.websocket
from tornado import gen
import re

cabx = 0 #servo1 90deg hosei
caby = 5 #servo2 90deg hosei
arduinousb = "/dev/ttyUSB0"

prog = re.compile(r'^[-+]*[0-9]+$')

def isInt(value): #SUUJI CHECK
    global prog
    if(prog.match(value) == None):
      return False
    else:
      return True

@gen.coroutine
def test_ws():
    global board, sv1, sv2
    client = yield tornado.websocket.websocket_connect("wss://amr-meiro.herokuapp.com/ws")
    client.write_message("C:Testing from client")

    l1 = True
    while True:
        msg = yield client.read_message()
        print("msg is %s" % msg)
        if msg.split(":")[0] == "D": #D ha data, C ha comment
            vx1 = msg.split(":")[2]
            if isInt(vx1): #SUIJI
                x1 = int(vx1)
                if x1 < -45: #45do ijyouha cut
                   x1 = -45
                if x1 > 45:
                   x1 = 45
                vy1 = msg.split(":")[3]
                if isInt(vy1): #SUIJI
                    y1 = int(vy1)
                    if y1 < -90:
                       y1 = -90
                    if y1 > 90:
                       y1 = 90
                    sv1.write(90 + cabx + round(x1 / 3, 0)) #/4 ha kando
                    sv2.write(90 + caby + round(y1 / 1, 0))
        board.digital[13].write(l1)
        l1 = not(l1)

    client.close() #not running

if __name__ == "__main__":
    print("INIT")
    board = Arduino(arduinousb)
    sv1 = board.get_pin('d:8:s')
    sv2 = board.get_pin('d:9:s')
    print("SERVO 90deg")
    sv1.write(90 + cabx)
    sv2.write(90 + caby)

    try:
        tornado.ioloop.IOLoop.instance().run_sync(test_ws)
    except KeyboardInterrupt:
        #client.close()
        print("ENDED")

