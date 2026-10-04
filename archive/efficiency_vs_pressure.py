import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

def comp(T1, P1, P2, eta=0.80):
    h1 = PropsSI("H", "T", T1, "P", P1, FLUID)
    s1 = PropsSI("S", "T", T1, "P", P1, FLUID)
    h2s = PropsSI("H", "P", P2, "S", s1, FLUID)
    h2 = h1 + (h2s - h1) / eta
    T2 = PropsSI("T", "P", P2, "H", h2, FLUID)
    return T2, h2, (h2 - h1)

def turb(T3, P3, P4, eta=0.85):
    h3 = PropsSI("H", "T", T3, "P", P3, FLUID)
    s3 = PropsSI("S", "T", T3, "P", P3, FLUID)
    h4s = PropsSI("H", "P", P4, "S", s3, FLUID)
    h4 = h3 - eta * (h3 - h4s)
    T4 = PropsSI("T", "P", P4, "H", h4, FLUID)
    return T4, h4, (h3 - h4)

# Fixed conditions (same as before)
T1 = 35 + 273.15
T3 = 150 + 273.15
P_low = 80e5
m_dot = 20.0  # not needed for efficiency, but kept for consistency

# Sweep high pressure
P_high_bar = np.arange(120, 301, 10)
eta_list = []

for P_h in P_high_bar:
    P_high = P_h * 1e5

    # Compressor 1->2
    T2, h2, w_c = comp(T1, P_low, P_high)

    # Heater 2->3 (set T3)
    h3 = PropsSI("H", "T", T3, "P", P_high, FLUID)
    q_in = h3 - h2

    # Turbine 3->4
    T4, h4, w_t = turb(T3, P_high, P_low)

    # Efficiency
    w_net = w_t - w_c
    eta = w_net / q_in
    eta_list.append(eta)

# Plot (save + close to avoid GUI errors)
plt.figure()
plt.plot(P_high_bar, eta_list)
plt.xlabel("High Pressure P_high (bar)")
plt.ylabel("Thermal Efficiency (-)")
plt.title("Efficiency vs High Pressure")
plt.grid(True)
plt.tight_layout()
plt.savefig("efficiency_vs_high_pressure.png", dpi=300)
plt.close()

print("Saved: efficiency_vs_high_pressure.png")
