# subslotNDT
A subslot-based numerical simulator for computing the Neighbor Discovery Time in schedule-based asynchronous duty cycling Wireless Sensor Networks

This repository contains supporting material to the research that based the paper "A new methodology for evaluating the Neighbor Descovery Time in schedule-based asynchronous duty-cycling Wireless Sensor Networks", currently under submission to the [MethodsX](https://www.sciencedirect.com/journal/methodsx) journal. More specifically:

- `ndtSim.py`: a numerical simulator to compute/estimate the NDT (Neighbor Discovery Time) between two sensors operating under (potentially different) wake-up schedules in a schedule-based asynchronous duty cycling Wireless Sensor Network. Differently from other simulators, this simulator operates on the level of subslots (i.e., it subdivides each slot of the schedule into smaller units) as to provide more temporal resolution.
- `runExp.sh`: a shell-script that runs the simulator with the several different parametrizations used on the experiments reported on the paper. The results reported on the paper can be reproduced by running this script.
- `plots.py`: uses matplotlib to plot several graphs to validade the subslot methodology proposed on the paper. This can be used to reproduce the graphs of the paper (assuming that `runExp.sh` has been executed before).

## Running the simulator

The `ndtSim.py` accepts a number of command line options. The available options can be seen by using the `-h` option:

```
usage: ndtSim.py [-h] [--samples file] [--bidirectional] [--duration duration] schA schB p reps [subslots]

Computes NDT statistics for (potentially asymmetric) schedules based on numerical simulations.

positional arguments:
  schA                  Schedule for the first sensor. Format: va,sa1[,sa2[,sa2...], where va is the cycle length, sa1,sa2,... are the indexes for the active slots
  schB                  Schedule for the second sensor. Format: vb,sb1[,sb2[,sb2...], where vb is the cycle length, sb1,sb2,... are the indexes for the active slots
  p                     sucess probability for the link
  reps                  number of repetitions for the simulation
  subslots              number of subslots to use to subdivide each slot. Defaults to 1.

options:
  -h, --help            show this help message and exit
  --samples file, -s file
                        name of the file to be generated with the NDT samples obtained in the simulation. If '-' is specified, the samples are printed to the stdout. If the option is omitted, samples are not
                        output.
  --bidirectional, -b   simulates in bidirectional discovery mode. Defaults to unidirecional.
  --duration duration, -d duration
                        duration of a transmission, in subslots. Defaults to 1.

```

For instance, to run 1000 simulations in which both sensors use a {7,3,1} Block Design with a link with a 0.8 success probability and considering a resolution of 10 subslots per slot in unidirecional mode, one can use the following command:

```
# python3 ndtSim.py 7,0,1,3 7,0,1,3 0.8 1000 10

Processing: [########################################] 1000/1000 -- Time (Elapsed/Remaining): 00:00/00:00

Statistics:
	- Minimum NDT: 0.0
	- Maximum NDT: 27.0
	- Mean NDT: 4.6708
		* Confidence interval: [4.42300384 4.91859616]
```

# Dependencies

The simulator was written in Python 3 and uses numpy and scipy. The script `plots.py` also uses Python 3 and depends on matplotlib, numpy, scipy and pandas.

