"""
suffix_automaton.py

This module contains the implementation of a suffix automaton for the "Dataset Synthesis Framework".

The following code has been translated and adapted from a C++ implementation available at: https://cp-algorithms.com/string/suffix-automaton.html

Original Contributors: [jakobkogler, mhayter, AtharvaThorve, iagorr, adamant-pwn, roll-no-1, wilsjame, lr1d, abeaumont, rohaquinlop, Kakalinn, hieplpvip, wikku, NAbdulla1]
Original License: Creative Commons Attribution Share Alike 4.0 International

Translator: Benjamin Koch
Date: 17 June 2025

License: This work is licensed under the Creative Commons Attribution Share Alike 4.0 International license. To view a copy of this license, visit https://creativecommons.org/licenses/by-sa/4.0/

Changes: Apart from choosing a dynamic array to store the states, utilizing __slots__ for memory savings, adding time measurements for the individual steps and decoupling a build_sa function from the lcs function for ease of use, no changes were made that were not strictly necessary for the translation from C++ to Python.
"""

# Imports
import time


class State:
    __slots__ = ["len", "link", "next"]

    def __init__(self):
        self.len = 0
        self.link = -1
        self.next = {}


class SuffixAutomaton:
    def __init__(self):
        self.states = []
        self.size = 0
        self.last = 0

    def init(self):
        self.states = [State()]
        self.size = 1
        self.last = 0

    def sa_extend(self, c):
        curr = self.size
        self.size += 1
        self.states.append(State())
        self.states[curr].len = self.states[self.last].len + 1
        p = self.last

        while p != -1 and c not in self.states[p].next:
            self.states[p].next[c] = curr
            p = self.states[p].link

        if p == -1:
            self.states[curr].link = 0
        else:
            q = self.states[p].next[c]

            if self.states[p].next[c] + 1 == self.states[q].len:
                self.states[curr].link = q
            else:
                clone = self.size
                self.size += 1
                self.states.append(State())
                self.states[clone].len = self.states[p].len + 1
                self.states[clone].next = self.states[q].next.copy()
                self.states[clone].link = self.states[q].link

                while p != -1 and self.states[p].next[c] == q:
                    self.states[p].next[c] = clone
                    p = self.states[p].link

                self.states[q].link = self.states[curr].link = clone

        self.last = curr

    def lcs(self, t):
        print(
            f"{'\033[34m'}Querying suffix automaton for longest common substring computation...{'\033[0m'}")
        start_time = time.time()

        v = 0
        l = 0
        best = 0
        bestpos = 0

        for i in range(len(t)):
            while v != 0 and t[i] not in self.states[v].next:
                v = self.states[v].link
                l = self.states[v].len

            if t[i] in self.states[v].next:
                v = self.states[v].next[t[i]]
                l += 1

            if l > best:
                best = l
                bestpos = i

        end_time = time.time()
        print(
            f"{'\033[34m'}Finished querying suffix automaton for longest common substring computation in {end_time - start_time} seconds...{'\033[0m'}")

        return t[bestpos - best + 1: bestpos + 1]

    def build_sa(self, s):
        print(
            f"{'\033[34m'}Building suffix automaton for document corpus...{'\033[0m'}")
        start_time = time.time()

        self.init()

        for c in s:
            self.sa_extend(c)

        end_time = time.time()
        print(
            f"{'\033[34m'}Finished building suffix automaton for document corpus in {end_time - start_time} seconds...{'\033[0m'}")
