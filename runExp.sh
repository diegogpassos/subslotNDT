#!/bin/bash

LONGSCHED="9507,0,1,3,37,52,191,308,332,433,914,919,984,1093,1155,1231,1238,1600,1678,1723,1732,1755,1773,1826,1930,1938,2099,2116,2141,2457,2712,2859,3058,3187,3466,3524,3655,3675,3748,4139,4145,4183,4297,4301,4518,4528,4600,4720,4777,4964,5043,5054,5176,5268,5329,5356,5496,5526,5601,5617,5851,6151,6173,6491,6539,6759,6778,6792,6878,7021,7163,7226,7290,7490,7650,7747,7860,7941,8028,8056,8154,8304,8339,8370,8438,8450,8505,8534,8574,8797,9005,9048,9094,9107,9133,9154,9270,9326,9400"
SCHED=133,0,9,10,12,26,30,67,74,82,109,114,120
SHORTSCHED="7,0,1,3"
REPS=1000000

# Validate that in the unidirectional discovery mode NDT is mostly unchanged between methodologies
for p in 0.4 0.7
do
	for s in 1 5 10 15 20
	do
		echo "p = $p, s = $s"
		python3 ./ndt_v4.py $LONGSCHED $LONGSCHED $p $REPS $s -s samples_p${p}_s${s}_dc1.03.dat
	done
done

# Validate that, for p = 1, in the unidirectional discovery mode, NDT increases by 0.5 slot in the proposed methodology with large s.
for s in 1 5 10 15 20 50 100
do
	echo "p = 1, s = $s, dc = 9.02"
	python3 ./ndt_v4.py $SCHED $SCHED 1 $REPS $s -s samples_p1_s${s}_dc9.02.dat
	echo "p = 1, s = $s, dc = 42.5"
	python3 ./ndt_v4.py $SHORTSCHED $SHORTSCHED 1 $REPS $s -s samples_p1_s${s}_dc42.5.dat
done

# Validate that, for p = 1, in the bidirectional discovery mode, NDT decreases in the proposed methodology with large s.
for s in 1 5 10 15 20 50 100
do
	echo "p = 1, s = $s, dc = 9.02"
	python3 ./ndt_v4.py -b $SCHED $SCHED 1 $REPS $s -a bsamples_p1_s${s}_dc9.02.dat
	echo "p = 1, s = $s, dc = 42.5"
	python3 ./ndt_v4.py -b $SHORTSCHED $SHORTSCHED 1 $REPS $s -s bsamples_p1_s${s}_dc42.5.dat
done

# Validate that, for low probabilities, in the bidirectional discovery mode, NDT drops by approx. half as s grows.
for s in 1 5 10 15 20 50 100
do
	echo "p = 0.1, s = $s, dc = 9.02"
	python3 ./ndt_v4.py -b $SCHED $SCHED 0.1 $REPS $s -s bsamples_p0.1_s${s}_dc9.02.dat
done


