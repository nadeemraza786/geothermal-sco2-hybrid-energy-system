# t2_t4_vs_phigh.py
# Plots (and saves) Compressor outlet temperature T2 and Turbine outlet temperature T4 vs high pressure P_high

import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

def comp(T1, P1, P2, eta=0.80):
    h1 = PropsSI("H", "T", T1, "P", P1, FLUID)
    s1 = PropsSI("S", "T", T1, "P", P1, FLUID)
    h2s = PropsSI("H", "P", P2, "S", s1, FLUID)   # isentropic outlet
    h2  = h1 + (h2s - h1) / eta                   # real outlet
    T2  = PropsSI("T", "P", P2, "H", h2, FLUID)
    return T2, h2

def turb(T3, P3, P4, eta=0.85):
    h3 = PropsSI("H", "T", T3, "P", P3, FLUID)
    s3 = PropsSI("S", "T", T3, "P", P3, FLUID)
    h4s = PropsSI("H", "P", P4, "S", s3, FLUID)   # isentropic outlet
    h4  = h3 - eta * (h3 - h4s)                   # real outlet
    T4  = PropsSI("T", "P", P4, "H", h4, FLUID)
    return T4, h4

# ---- Fixed conditions (same as your study) ----
T1 = 35 + 273.15          # K (compressor inlet)
T3 = 150 + 273.15         # K (turbine inlet)
P_low = 80e5              # Pa

# ---- Sweep high pressure ----
P_high_bar = np.arange(120, 301, 10)
T2_list_C = []
T4_list_C = []

for P_h in P_high_bar:
    P_high = P_h * 1e5

    # 1->2 compressor outlet temperature
    T2, h2 = comp(T1, P_low, P_high)

    # 3->4 turbine outlet temperature
    T4, h4 = turb(T3, P_high, P_low)

    T2_list_C.append(T2 - 273.15)
    T4_list_C.append(T4 - 273.15)

# ---- Plot + save (no plt.show to avoid GUI errors) ----
plt.figure()
plt.plot(P_high_bar, T2_list_C, label="T2 (after compressor)")
plt.plot(P_high_bar, T4_list_C, label="T4 (after turbine)")
plt.xlabel("High Pressure $P_{high}$ (bar)")
plt.ylabel("Temperature (°C)")
plt.title("T2 and T4 vs High Pressure")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("t2_t4_vs_phigh.png", dpi=300)
plt.close()

print("Saved: t2_t4_vs_phigh.png")
