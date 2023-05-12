from threading import Thread
from time import sleep

def th1 ():
    counter = 0
    while True:
        counter += 1
        print (counter)
        sleep(1)    

t1 = Thread(target=th1)
t2 = Thread(target=th1)
t3 = Thread(target=th1)
t4 = Thread(target=th1)

t1.start()
t2.start()
t3.start()
t4.start()