# Vincent Chau 998947424, Kevin Chan 999109300
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import simpy
import random
import math

SIM_TIME = 1000000
# Initialize global containers
exponentialArr = [0.0 for x in range(9)]
linearArr = [0.0 for x in range(9)]
exponentialEthernet = [0.0 for x in range(9)]
linearEthernet = [0.0 for x in range(9)]
""" Ethernet system  """
class Ethernet:
    def __init__(self, env, arrival_rate, hostNumber, backoff): # Initialize Object
        self.env = env
        self.backoff = backoff
        self.Hosts = [Host(env, i, backoff, arrival_rate) for i in range(10)] 
        self.action = env.process(self.run())
        self.hostNumber = hostNumber
        self.numCollisions = 0
        self.numSuccess = 0
    def run(self):
        while True:
            numberOfHostSending = 0
            collisionFlag = False
            i = 0
            while (i < 10): # Check all hosts
                self.Hosts[i].lengthPkt = self.Hosts[i].lengthPkt + self.Hosts[i].arrival_rate # Increment L
                if(((self.Hosts[i].lengthPkt < 1) or (self.env.now != self.Hosts[i].slotNumber))): # Not in this slot or length 0
                    if(self.Hosts[i].slotNumber <= self.env.now):
                        self.Hosts[i].slotNumber = self.env.now + 1  # Past the slot, increment it
                        self.Hosts[i].canTransmitFlag = False
                elif((self.Hosts[i].lengthPkt > 1) and (self.env.now == self.Hosts[i].slotNumber)):
                	self.Hosts[i].canTransmitFlag = True # Current host can transmit
                if (self.Hosts[i].canTransmitFlag == True):
                    numberOfHostSending = numberOfHostSending + 1 # Increment Ethernet's counter for the amount of host that is ready to send
                    hostIndex = i
                    if (numberOfHostSending > 1):
                        collisionFlag = True # More than one host trying to send!
                i = i + 1
            if (numberOfHostSending != 1): 
                if(collisionFlag == True): # Collision!
                    j = 0
                    while (j < 10):
                        if(self.Hosts[j].canTransmitFlag == True):
                            self.Hosts[j].slotNumber = self.Hosts[j].collision() # Run Exponential Backoff
                            self.numCollisions = self.numCollisions + 1
                        j = j + 1
            else: # Successfully transmitted packet, only one host trying to send
                if(self.backoff == "Exponential"):
                    exponentialArr[self.hostNumber] = exponentialArr[self.hostNumber] + 1
                elif(self.backoff == "Linear"):
                    linearArr[self.hostNumber] = linearArr[self.hostNumber] + 1
                self.Hosts[hostIndex].lengthPkt = self.Hosts[hostIndex].lengthPkt - 1 # Decrement the sent packet
                self.Hosts[hostIndex].slotNumber = self.env.now + 1 # Increment Slot number after sent
                self.Hosts[hostIndex].numberOfRetry = self.Hosts[hostIndex].numberOfRetry = 0 # Set N = 0 after sent
                self.Hosts[hostIndex].canTransmitFlag = False
                self.numSuccess = self.numSuccess + 1
            yield self.env.timeout(1) # reset
""" Host class """
class Host:
    def __init__(self, env, hostNum, backoff,arrival_rate):
        self.env = env
        self.arrival_rate = arrival_rate
        self.hostNum = hostNum
        self.lengthPkt = 0
        self.numberOfRetry = 0
        self.slotNumber = 0
        self.canTransmitFlag = False
        self.backoff = backoff # Exponential or Linear
    def collision(self):
        value = {
            "Linear" : self.env.now + 1 + random.randint(self.numberOfRetry, 1024), # K = min(n,1024)
            "Exponential" : self.env.now + 1 + random.randint(0, 2**(min(self.numberOfRetry, 10))) # 2^K K= min(n,10)
        } 
        increment = value[self.backoff]
        self.numberOfRetry = self.numberOfRetry + 1
        self.canTransmitFlag = False
        return(increment)
def main():
    env = simpy.Environment()
    print("=================Enthernet Simulation with 10 hosts=================\n")
    hostNum = 0
    currentEthernet = 0
    for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
        exponentialEthernet[currentEthernet] = Ethernet(env, arrival_rate, hostNum, "Exponential")
        linearEthernet[currentEthernet] = Ethernet(env, arrival_rate, hostNum, "Linear")
        hostNum = hostNum + 1 
        currentEthernet = currentEthernet + 1
    env.run(until=SIM_TIME)
    print("=================Exponential Backoff=================")
    print("Lambda:  [0.010, 0.0200, 0.0300, 0.0400, 0.0500, 0.0600, 0.0700, 0.0800, 0.0900]")
    throughputArr3 = [exponentialArr[i]/SIM_TIME for i in range(9)];
    print("Throughput: ", throughputArr3)
    print("\n=================Linear Backoff=================")
    print("Lambda:  [0.010, 0.0200, 0.0300, 0.0400, 0.0500, 0.0600, 0.0700, 0.0800, 0.0900]")
    throughputArr4 = [linearArr[i]/SIM_TIME for i in range(9)];
    print("Throughput: ", throughputArr4)

if __name__ == '__main__': main()