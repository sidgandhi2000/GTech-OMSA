import simpy
import random

#Constants and Global Variables

numBPCheck = 5 # Number of our ID/Boarding-Pass Checkers
numScan = 5 # Number of our scanners

arrivalRate = 5 # Arrival rate based on question prompt
checkRate = 0.75 # BP check rate
minScan = 0.5 # Min time for scanner, unif dist.
maxScan = 1.0 # Max time for scanner, unif dist.
runTime = 840 # Run time in minutes/simulation
rep = 100 # Number of replications

avgCheckTime = []
avgScanTime = []
avgWaitTime = []
avgSystemTime = []

#Generate the model
class System(object):
    def __init__(self, env):
        self.env = env
        self.checker = simpy.Resource(env, numBPCheck)
        self.scanner = []
        for i in range(numScan):
            self.scanner.append(simpy.Resource(env,1))

    def check(self, passenger):
        yield self.env.timeout(random.expovariate(1.0/checkRate))


    def scan(self, passenger):
        yield self.env.timeout(random.uniform(minScan, maxScan))

def passenger(env, name, s):
    global checkWait
    global scanWait
    global sysTime
    global totThrough

    timeArrive = env.now

    with s.checker.request() as request:
        yield request
        tIn = env.now
        yield env.process(s.check(name))
        tOut = env.now
        checkTime.append(tOut-tIn)

    minq = 0
    for i in range(1, numScan):
        if (len(s.scanner[i].queue) < len(s.scanner[minq].queue)):
            minq = i

    with s.scanner[minq].request() as request:
        yield request
        tIn = env.now
        yield env.process(s.scan(name))
        tOut = env.now
        scanTime.append(tOut - tIn)

    timeLeave = env.now
    sysTime.append(timeLeave - timeArrive)
    totThrough += 1

def setup(env):
    i = 0
    s = System(env)
    while True:
        yield env.timeout(random.expovariate(arrivalRate))
        i += 1

        env.process(passenger(env, 'Passenger %d' % i,s))

#Run the Model
for i in range(rep):
    random.seed(i)
    env = simpy.Environment()

    totThrough = 0
    checkTime = []
    scanTime = []
    sysTime = []

    env.process(setup(env))
    env.run(until=runTime)

    avgSystemTime.append(sum(sysTime[1:totThrough])/totThrough)
    avgCheckTime.append(sum(checkTime[1:totThrough])/totThrough)
    avgScanTime.append(sum(scanTime[1:totThrough])/totThrough)
    avgWaitTime.append(avgSystemTime[i] - avgCheckTime[i] - avgScanTime[i])


    print('%d : Replication %d times %.2f %.2f %.2f %.2f' % (totThrough,i+1,avgSystemTime[i],avgCheckTime[i],avgScanTime[i],avgWaitTime[i]))

# Calculate overall averages across all replications

print('-----')    
print('Average system time = %.2f' % (sum(avgSystemTime)/rep))
print('Average check time = %.2f' % (sum(avgCheckTime)/rep))
print('Average scan time = %.2f' % (sum(avgScanTime)/rep))
print('Average wait time = %.2f' % (sum(avgWaitTime)/rep))