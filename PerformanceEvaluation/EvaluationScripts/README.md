# How to Evaluate Results from Evaluation

Basically, the evaluation consists of two steps: First, the results from all single runs are preprocessed and so-called `average.json`-files are created. These contains the relevent data from one run. In the second step, the average-files are collected and visualized in one chart.

## Extract Relevant Data from Runs

Therefore, the Python Script `average-calculation.py` can be used. It has to be executed for every single simulation run. In order to automize this process, a number of unix commands are used:

	# Go to folder containing all results
	cd result/containing/folder
	# Execute python script for multiple runs in parallel
	find . | grep nfd.log | xargs -I {} -P 10 python path/to/evaluation/script/average-calculation.py {}

## Draw graphs

	# Stay in the folder which contains the results of all settings
	python path/to/evaluation/script/draw-graphs.py .

Now, the current folder should contain all relevant charts.
