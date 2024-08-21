import sys
from random import random
import math
import argparse
import numpy as np 
from scipy.stats import t
import time

def intconfBootstrapping(samples, confidence):

	x = np.array(samples)
	values = [np.random.choice(x,size=len(x),replace=True).mean() for i in range(1000)] 
	return np.percentile(values,[100*(1-confidence)/2,100*(1-(1-confidence)/2)]) 

def intconf(samples, confidence):

	x = np.array(samples)
	m = x.mean() 
	s = x.std() 
	dof = len(x) - 1
	t_crit = np.abs(t.ppf((1-confidence)/2,dof))

	return np.array([m-s*t_crit/np.sqrt(len(x)), m+s*t_crit/np.sqrt(len(x))])

def progressbar(it, prefix="", size=60, out=sys.stdout):

    start = time.time()
    elapsed = 0
    estimated = 0
    count = len(it)

    def sec2HMS(t):
        s = round(t) % 60
        m = round(t / 60) % 60
        h = round(t / 3600)

        if h == 0:
            return "{:02d}:{:02d}".format(m, s)
        else:
            return "{:02d}:{:02d}:{:02d}".format(h, m, s)

    def show(j, elapsed, estimated):
        x = int(size*j/count)
        print("{}[{}{}] {}/{} -- Time (Elapsed/Remaining): {}/{}".format(prefix, "#"*x, "."*(size-x), j, count, sec2HMS(elapsed), sec2HMS(estimated)), 
                end='\r', file=out, flush=True)
    show(0, elapsed, estimated)
    for i, item in enumerate(it):
        yield item
        if i % 10 == 0:
            now = time.time()
            elapsed = now - start
            estimated = elapsed / (i + 1) * (count - (i + 1))

        show(i+1, elapsed, estimated)
    print("\n", flush=True, file=out)

def parseArgs():

	parser = argparse.ArgumentParser(description='Computes NDT statistics for (potentially asymmetric) schedules based on numerical simulations.')
	parser.add_argument('schAString', metavar='schA', nargs=1,
						help='Schedule for the first sensor. Format: va,sa1[,sa2[,sa2...], where va is the cycle length, sa1,sa2,... are the indexes for the active slots')
	parser.add_argument('schBString', metavar='schB', nargs=1,
						help='Schedule for the second sensor. Format: vb,sb1[,sb2[,sb2...], where vb is the cycle length, sb1,sb2,... are the indexes for the active slots')
	parser.add_argument('p', metavar='p', type=float, nargs=1,
						help='sucess probability for the link')
	parser.add_argument('reps', metavar='reps', type=int, nargs=1,
						help='number of repetitions for the simulation')
	parser.add_argument('subslots', metavar='subslots', type=int, nargs='?', default=1,
						help='number of subslots to use to subdivide each slot. Defaults to 1.')
	parser.add_argument('--samples', '-s', metavar='file', default='',
						help='name of the file to be generated with the NDT samples obtained in the simulation. If \'-\' is specified, the samples are printed to the stdout. If the option is omitted, samples are not output.')
	parser.add_argument('--bidirectional', '-b', action='store_true',
						help='simulates in bidirectional discovery mode. Defaults to unidirecional.')
	parser.add_argument('--duration', '-d', metavar='duration', type=int, default=1,
						help='duration of a transmission, in subslots. Defaults to 1.')

	args = parser.parse_args()

	schA = [int(i) for i in args.schAString[0].split(",")]
	schB = [int(i) for i in args.schBString[0].split(",")]
	p = args.p[0]
	reps = args.reps[0]
	subslots = args.subslots
	samplesFile = args.samples

	va = schA[0] * subslots
	vb = schB[0] * subslots
	masterSlotsA = [True if j == 0 else False for i in schA[1:] for j in range(subslots)]
	masterSlotsB = [True if j == 0 else False for i in schB[1:] for j in range(subslots)]
	schA = [i*subslots + j for i in schA[1:] for j in range(subslots)]
	schB = [i*subslots + j for i in schB[1:] for j in range(subslots)]

	params = {

		"p": p,
		"va": va,
		"vb": vb,
		"schA": schA,
		"schB": schB,
		"reps": reps,
		"subslots" : subslots,
		"samplesFile" : samplesFile,
		"masterSlotsA" : masterSlotsA,
		"masterSlotsB" : masterSlotsB,
		"transmissionDuration": args.duration,
        "bidirectional" : args.bidirectional
	}

	return params

# Given the current slot, returns the index of the next active slot in sch.
def nextActiveSlot(slot, sch):

	for i in range(len(sch)):

		if slot <= sch[i]:
			return i 
	
	return 0

# Returns the difference between two slots, considering the cycle length.
def timeUntilSlot(currentSlot, targetSlot, v):

	diff = targetSlot - currentSlot
	if diff < 0:
		diff = v + diff
	return diff

# Performs a single repetition of the NDT simulaton
def simNDT(va, schA, masterSlotsA, vb, schB, masterSlotsB, p, transmissionDuration, bidirectional = False):

	# Store the simulation elapsed time in variable t
	t = 0

	# Keep in a variable the time elapsed since the last encounter opportunity.
	# This will be used to detect lack of rotation closure in the schedules.
	timeSinceLastOpportunity = 0

	# For the same purpose, compute the MMC between the lengths of the
	# schedules. This value represents the maximum time until an encounter 
	# opportunity happens (assuming rotation closure).
	maxIntervalUntilOpportunity = math.lcm(va, vb)

	# Ramdomly choose initial slots for each sensor.
	slotA = math.floor(random() * va)
	slotB = math.floor(random() * vb)
	initSlotA = slotA
	initSlotB = slotB

	# Find out the next active slot for each sensor.
	nextActiveA = nextActiveSlot(slotA, schA)
	nextActiveB = nextActiveSlot(slotB, schB)

	# Repeat until an encounter happens:
	while True:

		# Compute how long until the next active slot for any of the two nodes.
		timeUntilNextActive = min(timeUntilSlot(slotA, schA[nextActiveA], va), timeUntilSlot(slotB, schB[nextActiveB], vb))

		# Advance the simulation time until that next active slot.
		t = t + timeUntilNextActive
		slotA = (slotA + timeUntilNextActive) % va
		slotB = (slotB + timeUntilNextActive) % vb
		
		# For each sensor, check if the next slot is active.
		if slotA == schA[nextActiveA]:

			# Yes.
			activeSlotA = True

			# Check if this is a transmission subslot for A.
			if masterSlotsA[nextActiveA]:
				transmissionSlotA = True
			else:
				transmissionSlotA = False

			# Find out A's next active slot (after this one).
			nextActiveA = (nextActiveA + 1) % len(schA)
		else:

			# No.
			activeSlotA = False
			transmissionSlotA = False

		if slotB == schB[nextActiveB]:

			# Yes.
			activeSlotB = True

			# Check if this is a transmission subslot for B.
			if masterSlotsB[nextActiveB]:
				transmissionSlotB = True
			else:
				transmissionSlotB = False

			# Find out B's next active slot (after this one).
			nextActiveB = (nextActiveB + 1) % len(schB)
		else:

			# No.
			activeSlotB = False
			transmissionSlotB = False
		
		# Check if we have an encounter opportunity:
		# * In the unidirecional case:
		#  - both nodes are active.
		#  - A is in the first subslot of a slot.
		# * In the bidirecional case:
		#  - both nodes are active.
		#  - Either A or B is in the first subslot of a slot.
		opportunity = False
		if activeSlotA == True and activeSlotB == True and (transmissionSlotA or (transmissionSlotB and bidirectional)):

			# Yes. We still need to verify if the receiver will stay awake for enough
			# time to receive the frame. We do that by checking if the next (transmissionDuration-1) 
			# (sub)slots are consecutive. We have to evaluate that for both the cases of
			# A being the transmitter and B being the transmitter.
			if transmissionSlotA:
				opportunity = True
				for i in range(transmissionDuration-1):
					if schB[(nextActiveB + i) % len(schB)] != (slotB + i + 1) % vb:
						opportunity = False
						break
			if opportunity == False and transmissionSlotB:
				opportunity = True
				for i in range(transmissionDuration-1):
					if schA[(nextActiveA + i) % len(schA)] != (slotA + i + 1) % va:
						opportunity = False
						break

		# In conclusion, is this an encounter opportunity?
		if opportunity:

			# Yes. Randomly select a value in [0, 1) to dedice whether the 
			# communication was sucessful.
			if random() < p:

				# Yes, there was communication. End of this simulation repetition.
				return t, initSlotA, initSlotB

			# No. Update the time since the last opportunity.
			timeSinceLastOpportunity = 0

		else:

			# No, that was not an opportunity. Update the time since the last opportunity.
			timeSinceLastOpportunity = timeSinceLastOpportunity + timeUntilNextActive

			# Check if this time is larger than the theoretical maximum.
			if timeSinceLastOpportunity >= maxIntervalUntilOpportunity:
				# Yes, this means the schedules lack rotation closure.
				print("Schedules lack rotation closure: failure for offset {}".format(slotA - slotB))
				sys.exit(1)



# Parse arguments
params = parseArgs()
samples = [0] * params["reps"]
samplesSlotA = [0] * params["reps"]
samplesSlotB = [0] * params["reps"]

# Make the requested number of repetitions. Display a status bar to provide estimates for
# how long the execution will take.
print("")
for i in progressbar(range(params["reps"]), "Processing: ", 40):
	samples[i],samplesSlotA[i],samplesSlotB[i] = simNDT(params["va"], params["schA"], params["masterSlotsA"], 
						params["vb"], params["schB"], params["masterSlotsB"], 
						params["p"], params["transmissionDuration"], params["bidirectional"])

# End of repetitions. Compute and output statistics.
print("Statistics:")
print("\t- Minimum NDT: {}".format(min(samples) / float(params["subslots"])))
print("\t- Maximum NDT: {}".format(max(samples) / float(params["subslots"])))
print("\t- Mean NDT: {}".format((sum(samples) / float(params["reps"]) / float(params["subslots"]))))
print("\t\t* Confidence interval: {}".format(intconf(samples, 0.95) / float(params["subslots"])))
#print("\t\t* Confidence interval (Bootstrapping): {}".format(intconfBootstrapping(samples, 0.95) / float(params["subslots"])))

print("")

# If the user requested the output of the samples, do it now.
if params["samplesFile"] != "":
	if params["samplesFile"] == "-":
		print("#############")
		print("Samples:")
	else:
		f = open(params["samplesFile"], "w")
		sys.stdout = f

	for i in range(len(samples)):
		print(samplesSlotA[i], samplesSlotB[i], samples[i])
