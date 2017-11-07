import pygame
from pygame.locals import *

import math
import numpy
import pickle

import threading
import time
import Queue

import generator_cw


threadLock = threading.Lock()

#class myThread(threading.Thread):
#    def __init__(self, threadID, name, counter, delay, ear, fs, fc, message):
#        threading.Thread.__init__(self)
#        self.threadID = threadID
#        self.name = name
#        self.counter = counter
#        self.delay = float(delay)
#        self.ear = ear
#        self.fs = fs
#        self.fc = fc
#        self.message = message
#
#    def run(self):
#        threadLock.acquire()
#        play_sound(self.delay, self.counter, self.fs, self.fc, self.ear, self.message) #--- This already creates a thread!!!
#        print "Playing thread %s" % (self.name)
#        threadLock.release()


def play_sound(delay, num_repetitions, fs, fc, ear, message, noise=False, wpm=40, vol=(1, 1)):
    time.sleep(delay)
    m = generator_cw.message(message=message, fs=fs, fc=fc, amplitude=0.5, wpm=wpm, front_buffer=1, back_buffer=1, noise=noise, ear=ear)
    t_ms, buf = m.get()
    sound = pygame.sndarray.make_sound(buf)
    channel = sound.play(loops = (num_repetitions-1))
    channel.set_volume(vol[0],vol[1])
#    channel.stop()
    return t_ms, channel


def mute_background(bkg_channel, t_ms, vol):
    bkg_channel.set_volume(0, 0)
    time.sleep(t_ms/1.e3)
    bkg_channel.set_volume(vol[0], vol[1])


def main():
    fs = 8000
    fc = 900
    size = (800, 600)
    bits = 16
    background_color = (255, 255, 255)

    wpm = 40
    callsign = 'ea3alz'
    zone = 14

    pygame.mixer.pre_init(fs, -bits, 2)
    pygame.init()

    screen = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF)
    screen.fill(background_color)
    pygame.display.set_caption("SO2R trainer")

#    # buttons
#    button_F1_L = pygame.draw.rect(screen,(211,211,211),(size[0]*0.05, size[1]*0.9, size[0]*0.1, size[1]*0.04));
#    button_F2_L = pygame.draw.rect(screen,(211,211,211),(size[0]*0.16, size[1]*0.9, size[0]*0.1, size[1]*0.04));
#    button_F3_L = pygame.draw.rect(screen,(211,211,211),(size[0]*0.27, size[1]*0.9, size[0]*0.1, size[1]*0.04));
#    button_F4_L = pygame.draw.rect(screen,(211,211,211),(size[0]*0.38, size[1]*0.9, size[0]*0.1, size[1]*0.04));
#    button_F5_L = pygame.draw.rect(screen,(211,211,211),(size[0]*0.05, size[1]*0.95, size[0]*0.1, size[1]*0.04));
#    button_F6_L = pygame.draw.rect(screen,(211,211,211),(size[0]*0.16, size[1]*0.95, size[0]*0.1, size[1]*0.04));
#    button_F7_L = pygame.draw.rect(screen,(211,211,211),(size[0]*0.27, size[1]*0.95, size[0]*0.1, size[1]*0.04));
#    button_F8_L = pygame.draw.rect(screen,(211,211,211),(size[0]*0.38, size[1]*0.95, size[0]*0.1, size[1]*0.04));
#
#    line_separation = pygame.draw.line(screen, (0, 0, 0), (size[0]*0.5, 0), (size[0]*0.5, size[1]))
#
#    button_F1_R = pygame.draw.rect(screen,(211,211,211),(size[0]*0.52, size[1]*0.9, size[0]*0.1, size[1]*0.04));
#    button_F2_R = pygame.draw.rect(screen,(211,211,211),(size[0]*0.63, size[1]*0.9, size[0]*0.1, size[1]*0.04));
#    button_F3_R = pygame.draw.rect(screen,(211,211,211),(size[0]*0.74, size[1]*0.9, size[0]*0.1, size[1]*0.04));
#    button_F4_R = pygame.draw.rect(screen,(211,211,211),(size[0]*0.85, size[1]*0.9, size[0]*0.1, size[1]*0.04));
#    button_F5_R = pygame.draw.rect(screen,(211,211,211),(size[0]*0.52, size[1]*0.95, size[0]*0.1, size[1]*0.04));
#    button_F6_R = pygame.draw.rect(screen,(211,211,211),(size[0]*0.63, size[1]*0.95, size[0]*0.1, size[1]*0.04));
#    button_F7_R = pygame.draw.rect(screen,(211,211,211),(size[0]*0.74, size[1]*0.95, size[0]*0.1, size[1]*0.04));
#    button_F8_R = pygame.draw.rect(screen,(211,211,211),(size[0]*0.85, size[1]*0.95, size[0]*0.1, size[1]*0.04));

    pygame.display.update();

    is_running = True
    is_sent = False

    # Background noise
    _, background_R = play_sound(delay=0, num_repetitions=0, fs=fs, fc=15, ear="R", message='eeeeeeeee', noise="0,1", wpm=10, vol=(0,0.2))
    _, background_L = play_sound(delay=0, num_repetitions=0, fs=fs, fc=15, ear="L", message='eeeeeeeee', noise="0,1", wpm=10, vol=(0.2,0))
    TX_R = None
    TX_L = None

    while is_running:

#        threads = []
#        if not is_sent:
#            thread1 = myThread(1, "thread1", 1, 0, "R", fs, fc, 'test ea3alz')
#            thread2 = myThread(2, "thread2", 1, 2, "L", fs, 1000, 'test k3lr')
#
#            thread1.start()
#            thread2.start()
#
#            threads.append(thread1)
#            threads.append(thread2)
#
#            is_sent = True
#
#        for t in threads:
#            t.join()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
                break

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_running = False

                elif event.key == pygame.K_F1:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        print "Shift+F1 pressed"
                        t_ms, TX_L = play_sound(delay=0, num_repetitions=1, fs=fs, fc=fc, ear="R+L", message='test ea3alz', noise=False, wpm=wpm, vol=(1,0))
                        mute_background(bkg_channel=background_L, t_ms=t_ms, vol=(0.2,0))
                    else:
                        print "F1 pressed"
                        t_ms, TX_R = play_sound(delay=0, num_repetitions=1, fs=fs, fc=fc, ear="R+L", message='test ea3alz', noise=False, wpm=wpm, vol=(0,1))
                        mute_background(bkg_channel=background_R, t_ms=t_ms, vol=(0,0.2))
                elif event.key == pygame.K_F2:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        print "Shift+F2 pressed"
                        TX_L = play_sound(delay=0, num_repetitions=1, fs=fs, fc=fc, ear="R+L", message=str('%s 5nn%d'%(callsign, zone)), noise=False, wpm=wpm, vol=(1,0))
                        mute_background(bkg_channel=background_L, t_ms=t_ms, vol=(0.2,0))
                    else:
                        print "F2 pressed"
                        TX_R = play_sound(delay=0, num_repetitions=1, fs=fs, fc=fc, ear="R+L", message=str('%s 5nn%d'%(callsign, zone)), noise=False, wpm=wpm, vol=(0,1))
                        mute_background(bkg_channel=background_R, t_ms=t_ms, vol=(0,0.2))
                elif event.key == pygame.K_F3:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        print "Shift+F3 pressed"
                        TX_L = play_sound(delay=0, num_repetitions=1, fs=fs, fc=fc, ear="R+L", message=str('tu %s'%callsign), noise=False, wpm=wpm, vol=(1,0))
                        mute_background(bkg_channel=background_L, t_ms=t_ms, vol=(0.2,0))
                    else:
                        print "F3 pressed"
                        TX_R = play_sound(delay=0, num_repetitions=1, fs=fs, fc=fc, ear="R+L", message=str('tu %s'%callsign), noise=False, wpm=wpm, vol=(0,1))
                        mute_background(bkg_channel=background_R, t_ms=t_ms, vol=(0,0.2))
                elif event.key == pygame.K_F4:
                    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                        print "Shift+F4 pressed"
                        TX_L = play_sound(delay=0, num_repetitions=1, fs=fs, fc=fc, ear="R+L", message=str('%s'%callsign), noise=False, wpm=wpm, vol=(1,0))
                        mute_background(bkg_channel=background_L, t_ms=t_ms, vol=(0.2,0))
                    else:
                        print "F4 pressed"
                        TX_R = play_sound(delay=0, num_repetitions=1, fs=fs, fc=fc, ear="R+L", message=str('%s'%callsign), noise=False, wpm=wpm, vol=(0,1))
                        mute_background(bkg_channel=background_R, t_ms=t_ms, vol=(0,0.2))

    pygame.quit()


main()
