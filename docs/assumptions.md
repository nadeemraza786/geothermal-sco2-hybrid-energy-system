# Model Assumptions

## Thermodynamic model

The working fluid is CO₂ and thermophysical properties are evaluated with CoolProp.

The baseline cycle uses fixed isentropic efficiencies for compressor and turbine.

Pressure losses across the geothermal heater, cooler and recuperator are neglected.

The recuperator is represented with a fixed effectiveness of 0.80.

Recuperation is enabled only when the turbine outlet temperature is higher than the compressor outlet temperature.

## Start up model

The start up study is quasi steady.

Pressure, turbine inlet temperature and mass flow are ramped with first order exponential functions.

At each time point the steady thermodynamic cycle is solved using the current ramped inputs.

The model does not include shaft inertia, component thermal mass, heat exchanger metal capacitance or transient CO₂ inventory.

## PV model

PV generation is based on PVGIS hourly resource data accessed through pvlib.

The reference PV system is 1 MWp with a performance ratio of 0.85, 30 degree tilt and south facing azimuth.

## Hybrid dispatch

The reference dispatch scenario uses constant geothermal generation, fixed electrical demand, hourly PV generation and battery storage.

Battery charge and discharge efficiencies are fixed at 0.95.

The supplied 8 MWh and 0.20 MW battery is a scenario assumption and is not claimed to be an optimized design.
