# Python Branch Prediction

Este es un programa de simulación para distintos tipos de predictores de saltos. En base a parametros definidos por el usuario, se simulan distintos tipos de preditores

## Predictores disponibles

Los predictores disponibles para su simulación son:

* Bimodal predictor
* Global history predictor (GShare)
* Private history predictor (PShare)
* Tournament predictor

## Ejecución

In order to execute the simulation, open a terminal on the source directory, and run `gunzip -c ./branch-trace-gcc.trace.gz | ./branch -s < # > -bp < # > -gh < # > -ph < # >`. Where 's' is the size of the BTH table, 'bp' is predictor type (accepted values are 0, 1, 2 and 3, corresponding to bimodal, global, private and tournament predictors respectively), 'gh' is the global prediction registry size, and 'ph' is the private prediction registry size.

## Requerimientos

1. Must have gzip installed
2. Must have Python 3 installed