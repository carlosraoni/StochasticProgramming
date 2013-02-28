#!/bin/bash

test_file=$1
empty=""

while read line
do
	if [[ "$line" == "$empty" ]] || [[ $line == \#* ]]; then 
		echo ""
	else
		name=`echo $line | cut -d ' ' -f 1`		
		dir=`echo $line | cut -d ' ' -f 2`
		core=`echo $line | cut -d ' ' -f 3`
		time=`echo $line | cut -d ' ' -f 4`
		stoch=`echo $line | cut -d ' ' -f 5`

		echo "Running Test: $dir $core $time $stoch"
		outfile="testResults/$name.out"
		./runSmpsTwoStageSolver.sh $dir $core $time $stoch > $outfile
		
		obj=`cat $outfile | grep Optimal | cut -d ' ' -f 4`
		echo "Optimal Solution: $obj"
		echo ""	
	fi
done < $test_file
