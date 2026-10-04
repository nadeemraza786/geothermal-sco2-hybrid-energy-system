# Model Equations

## Compressor

The real compressor outlet enthalpy is calculated from the isentropic outlet state.

h2 = h1 + (h2s minus h1) divided by eta_c

Specific compressor work:

w_c = h2 minus h1

## Turbine

The real turbine outlet enthalpy is:

h4 = h3 minus eta_t times (h3 minus h4s)

Specific turbine work:

w_t = h3 minus h4

## Net power

Specific net work:

w_net = w_t minus w_c

Net electrical power:

W_net = m_dot times w_net

## Geothermal heat input

Without recuperation:

q_in = h3 minus h2

With recuperation:

q_in = h3 minus h2r

Thermal efficiency:

eta_th = w_net divided by q_in

## Recuperator

The recuperator is only active when T4 is greater than T2.

The maximum cold side outlet enthalpy corresponds to the hot side inlet temperature at high pressure.

h2_max = h(P_high, T4)

Recovered specific heat:

q_recup = epsilon times (h2_max minus h2)

The cleaned portfolio model sets q_recup to zero when T4 is less than or equal to T2.

This correction is important because the original effectiveness expression can otherwise imply reverse heat recovery.

## Quasi steady start up

The original start up study uses exponential ramps:

x(t) = x_final times (1 minus exp(minus t divided by tau))

The approximate time to reach 95 percent of the final value is:

t_95 = minus tau times ln(0.05)

For the supplied time constants:

Pressure tau = 900 s, t_95 is about 45 min

Turbine inlet temperature tau = 1200 s, t_95 is about 60 min

Mass flow tau = 600 s, t_95 is about 30 min

The calculation is quasi steady. Each time point solves a steady thermodynamic state using the current ramped inputs.

## Hybrid dispatch

The electrical load is supplied in this order:

Geothermal baseload

Direct PV generation

Battery discharge

Grid import

Surplus PV first charges the battery. Remaining surplus is curtailed.

Battery energy update during charging:

E_next = E + eta_charge times P_charge times dt

Battery energy update during discharge:

E_next = E minus P_discharge times dt divided by eta_discharge
