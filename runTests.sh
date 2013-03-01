#!/bin/bash

test_file="test_instances.in"
instance_name=$1
instance_scenarios=$2
last_instance=""

while read line
do
	if [[ "$line" == "" ]] || [[ $line == \#* ]]; then 
		#echo ""
		:
	else
		name=`echo $line | cut -d ' ' -f 1`		
		scen=`echo $line | cut -d ' ' -f 2`		
		dir=`echo $line | cut -d ' ' -f 3`
		core=`echo $line | cut -d ' ' -f 4`
		time=`echo $line | cut -d ' ' -f 5`
		stoch=`echo $line | cut -d ' ' -f 6`

		if [ "$instance_name" == "" ] || [ "$instance_name" == "$name" ]; then
			if [ "$instance_scenarios" == "" ] || [ "$instance_scenarios" == "$scen" ]; then
				if [ "$name" != "$last_instance" ]; then
					echo ""					
					echo "$name ==================================================================="
				fi				
				
				echo "Running Test: $dir $core $time $stoch"
				outfile="testResults/$name-$scen.out"
				./runSmpsTwoStageSolver.sh $dir $core $time $stoch > $outfile
		
				obj=`cat $outfile | grep Optimal | cut -d ' ' -f 4`
				echo "$name $scen: $obj"
				echo ""
				last_instance=$name
			fi
		fi	
	fi
done < $test_file
