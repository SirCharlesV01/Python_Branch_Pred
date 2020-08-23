# Python branch prediction

This is a branch prediction simulation program. From a given trace file and user defined parameters, a cache with different types of available predictors is simulated.

## Available predictors

The predictors available for simulation are:

* Bimodal predictor
* Global history predictor
* Private history predictor
* Tournament predictor

## Execution

In order to execute the simulation, open a terminal on the source directory, and run `gunzip -c ./branch-trace-gcc.trace.gz | ./branch.py <s> <bp> <gh> <ph>`. Where 's' is the size of the BTH table, 'bp' is predictor type (accepted values are 0, 1, 2 and 3, corresponding to bimodal, global, private and tournament predictors respectively), 'gh' is the global prediction registry size, and 'ph' is the private prediction registry size. You could, for example execute `gunzip -c ./branch-trace-gcc.trace.gz | ./branch.py 4 0 4 3` to observe quick results