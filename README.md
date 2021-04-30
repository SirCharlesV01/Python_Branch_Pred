# Python Branch Prediction

This is a simulation program for various types of branch predictors. The different types of branch predictors implemented are simulated based on user defined parameters.

## Available predictors:

* Bimodal predictor
* Global history predictor (GShare)
* Private history predictor (PShare)
* Tournament predictor

## Simulation Parameters:

In order to execute the simulation, open a terminal on the source directory, and run `gunzip -c ./branch-trace-gcc.trace.gz | ./branch -s < # > -bp < # > -gh < # > -ph < # >`. Where 's' is the size of the BTH table, 'bp' is predictor type (accepted values are 0, 1, 2 and 3, corresponding to bimodal, global, private and tournament predictors respectively), 'gh' is the global prediction registry size, and 'ph' is the private prediction registry size.

## Requirements:

1. Must have gzip installed
2. Must have Python 3 installed
