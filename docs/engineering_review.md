# Engineering Review

## Main physical insights

### High pressure has an optimum

Increasing high pressure initially increases turbine expansion work. At the same time compressor work also rises.

The supplied net power curve therefore reaches a maximum and then decreases. This is a classic tradeoff between expansion benefit and compression penalty.

### Mass flow changes power almost linearly at fixed thermodynamic states

The supplied mass flow study keeps pressure and temperature fixed. Specific net work therefore remains almost constant and net power scales approximately with mass flow.

### Recuperation changes heat demand more than shaft work

In the idealized model the recuperator has no pressure drop and does not change compressor or turbine inlet states.

Therefore net shaft work is almost unchanged.

The main effect is lower geothermal heat input and higher thermal efficiency when useful temperature driving force exists.

### Recuperation is not feasible at every pressure

The supplied T2 and T4 plot shows compressor outlet temperature increasing with high pressure while turbine outlet temperature decreases.

At sufficiently high pressure the two temperatures cross.

When T4 is below T2, a conventional recuperator cannot preheat the compressed stream using turbine exhaust.

The cleaned model therefore disables recuperation in that region.

### Net power optimum and efficiency optimum are different objectives

A point that maximizes net power does not necessarily maximize thermal efficiency.

A professional optimization study should report the objective function explicitly.

### Start up results are quasi steady

The start up scripts ramp pressure, turbine inlet temperature and mass flow and then solve a steady cycle at each time point.

This is useful for control oriented and first order start up assessment.

It is not a full transient conservation model with component thermal capacitance, fluid inventory and rotating equipment inertia.

### Negative early start up efficiency is not a normal operating point

The original start up plot shows negative efficiency during the first minutes.

This occurs while compression work is required before useful turbine output and geothermal heat input establish a generating state.

The cleaned plotting logic omits thermal efficiency until the cycle has positive net power and positive heat input.

## Hybrid system interpretation

The full year hybrid script uses a constant geothermal baseload, hourly PV generation, battery charge and discharge, grid import and PV curtailment.

The supplied trial battery is 8 MWh with 0.20 MW power, corresponding to a nominal 40 hour energy to power duration.

This is a scenario assumption, not an optimized battery design.

Future work could optimize battery energy and power independently against renewable fraction, curtailment and grid import.
