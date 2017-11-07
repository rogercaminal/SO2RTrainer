import pygame
from pygame.locals import *

import math
import numpy
import pickle

import threading
import time

import generator_cw


threadLock = threading.Lock()

class myThread(threading.Thread):
    def __init__(self, threadID, name, counter, delay, ear, fs, fc, message):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.delay = float(delay)
        self.ear = ear
        self.fs = fs
        self.fc = fc
        self.message = message

    def run(self):
        threadLock.acquire()
        play_sound(self.delay, self.counter, self.fs, self.fc, self.ear, self.message)
        print "Playing thread %s" % (self.name)
        threadLock.release()


def play_sound(delay, counter, fs, fc, ear, message):
    while counter:
        time.sleep(delay)
        m = generator_cw.message(message=message, fs=fs, fc=fc, amplitude=0.5, wpm=40, front_buffer=10, back_buffer=10, noise=False, ear=ear)
        buf = m.get()
        sound = pygame.sndarray.make_sound(buf)
        sound.play(loops = 0)

        counter -= 1

def main():
    fs = 8000
    fc = 900
    size = (800, 600)
    bits = 16

    pygame.mixer.pre_init(fs, -bits, 2)
    pygame.init()

    _display_surf = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF)

    _running = True
    _sent = False
    while _running:

        threads = []

        if not _sent:
            thread1 = myThread(1, "thread1", 1, 0, "R+L", fs, fc, 'test ea3alz')
            thread2 = myThread(2, "thread2", 1, 2, "R+L", fs, 1000, 'test k3lr')

            thread1.start()
            thread2.start()

            threads.append(thread1)
            threads.append(thread2)

            _sent = True

        for t in threads:
            t.join()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _running = False
                break
    pygame.quit()


main()
