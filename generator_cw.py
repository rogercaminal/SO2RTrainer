from __future__ import division, print_function
import os, sys
import math
import numpy as np

class message(object):

    #_________________________________________________________________________________________________________
    def __init__(self, message="", fs=8000, fc=900, amplitude=0.5, wpm=20, front_buffer=2000, back_buffer=2000, noise=False, ear="R+L"):
        self.message       = message
        self.fs            = fs # hz
        self.fc            = fc # hz
        self.amplitude     = amplitude # max 1
        self.wpm           = wpm
        self.front_buffer  = front_buffer # quiet to append to the beginning of the output, in ms
        self.back_buffer   = back_buffer # quiet for the end, ms
        self.randoms       = list()
        self.compensated   = 0
        self.w_compensated = 0
        self.stats         = {}
        self.noise         = noise # mean,sd
        self.ear           = ear

        self.symbols = []
        self.voids = []

        self.output = []

        self.morse = {
            ".-" : "a", "-..." : "b", "-.-." : "c", "-.." : "d",
            "." : "e", "..-." : "f", "--." : "g", "...." : "h",
            ".." : "i", ".---" : "j", "-.-" : "k", ".-.." : "l",
            "--" : "m", "-." : "n", "---" : "o", ".--." : "p",
            "--.-" : "q", ".-." : "r", "..." : "s", "-" : "t",
            "..-" : "u", "...-" : "v", ".--" : "w", "-..-" : "x",
            "-.--" : "y", "--.." : "z", ".----" : "1", "..---" : "2",
            "...--" : "3", "....-" : "4", "....." : "5", "-...." : "6",
            "--..." : "7", "---.." : "8", "----." : "9", "-----" : "0",
            ".--.-." : "@", "---." : "!", "--..--" : ",", ".-.-.-" : ".",
            "..--.." : "?"
        }


    #_________________________________________________________________________________________________________
    def get(self):
        self.initialise()
        self.mkmorse()
        self.mkaudio()

        buf = np.zeros((len(self.output), 2), dtype = np.int16)
        renorm = (2**16)/2
        for i, b in enumerate(self.output):
            if self.ear=="R":
                buf[i][1] = int(round(b*renorm))
            elif self.ear=="L":
                buf[i][0] = int(round(b*renorm))
            elif self.ear=="R+L":
                buf[i][0] = int(round(b*renorm))
                buf[i][1] = int(round(b*renorm))

        return buf



    #_________________________________________________________________________________________________________
    def initialise(self):
        # element time based on http://www.kent-engineers.com/codespeed.htm
        elements_per_minute = float(self.wpm) * 50 # 50 codes in PARIS
        element_ms = float(60. / elements_per_minute) * 1000 # 60 seconds

        self.stats["dotavg"] = element_ms
        self.stats["dotsd"] = 0
        self.stats["dashavg"] = 3 * element_ms
        self.stats["dashsd"] = 0
        self.stats["inter_void_avg"] = element_ms
        self.stats["inter_void_sd"] = 0
        self.stats["letter_void_avg"] = 3 * element_ms
        self.stats["letter_void_sd"] = 0
        self.stats["word_void_avg"] = 7 * element_ms
        self.stats["word_void_sd"] = 0


    #_________________________________________________________________________________________________________
    def mkmorse(self):

        self.symbols = list()
        self.voids = list()
        inv_morse = {v:k for k, v in self.morse.items()}

        for e in self.message:
            if e != ' ':
                try:
                    m = inv_morse[e]
                except:
                    print("** Unknown character", e, "in message.  Update the dictionary.")
                    exit()

                for c in m:
                    if c == '.':
                        dot = self.stats["dotavg"]
                        inter_void = self.stats["inter_void_avg"]

                        self.symbols.append(dot)
                        self.voids.append(inter_void)

                    elif c == '-':
                        dash = self.stats["dashavg"]
                        inter_void = self.stats["inter_void_avg"]

                        self.symbols.append(dash)
                        self.voids.append(inter_void)

                    else:
                        print("** Bad symbol in dictionary lookup for", m)
                        exit()

                self.voids.pop(-1) # remove last inter_void
                letter_void = self.stats["letter_void_avg"]

                self.voids.append(letter_void)
            else: # space
                self.voids.pop(-1) # remove last letter_void
                word_void = self.stats["word_void_avg"]
                self.voids.append(word_void)

        self.voids.pop(-1) # take away the last void


    #_________________________________________________________________________________________________________
    def mkaudio(self):

        self.output = list()
        for x in range(int(self.front_buffer * (self.fs/1000))): # give some initial void to the output
            self.output.append(0)

        index = x
        for i in range(len(self.symbols)):
            limit = index + int(self.symbols[i] * (self.fs/1000))
            for x in range(index, limit):
                self.output.append(self.amplitude * math.sin(2.0 * np.pi * self.fc * (x % self.fc/self.fs)))
                index = index + limit

            if i < len(self.symbols)-1:
                limit = index + int(self.voids[i] * (self.fs/1000))

                for x in range(index, limit):
                    self.output.append(0)

                index = limit

        # ending void
        for x in range(index, index + int(self.back_buffer * (self.fs/1000))):
            self.output.append(0)

        self.output = np.array(self.output, dtype=float)

        if self.noise:
            try:
                self.noise.index(',')
            except:
                print("** -n argument requires average and standard deviation seperated by a comma, e.g. -n 0,2 - no spaces")
                exit()

            noise_avg, noise_sd = self.noise.split(',')
            noise_avg = float(noise_avg)
            noise_sd = float(noise_sd)

            # save the prng state
            r = np.random.RandomState()
            state = r.get_state()
            noise_rx = np.random.normal(noise_avg, noise_sd, len(self.output))
            r.set_state(state)

            # combine the gaussian noise with the output signal
            for i in range(len(self.output)):
                self.output[i] = self.output[i] + noise_rx[i]

