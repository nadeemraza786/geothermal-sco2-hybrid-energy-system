# turbine_compressor_vs_phigh.py
# Plots (and saves) Turbine Power and Compressor Power vs High Pressure for your simple sCO2 cycle

import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

def comp(T1, P1, P2, eta=0.80):
    h1 = PropsSI("H", "T", T1, "P", P1, FLUID)
    s1 = PropsSI("S", "T", T1, "P", P1, FLUID)
    h2s = PropsSI("H", "P", P2, "S", s1, FLUID)          # isentropic
    h2  = h1 + (h2s - h1) / eta                          # real
    T2  = PropsSI("T", "P", P2, "H", h2, FLUID)
    return T2, h2, (h2 - h1)                              # w_comp (J/kg)

def turb(T3, P3, P4, eta=0.85):
    h3 = PropsSI("H", "T", T3, "P", P3, FLUID)
    s3 = PropsSI("S", "T", T3, "P", P3, FLUID)
    h4s = PropsSI("H", "P", P4, "S", s3, FLUID)          # isentropic
    h4  = h3 - eta * (h3 - h4s)                          # real
    T4  = PropsSI("T", "P", P4, "H", h4, FLUID)
    return T4, h4, (h3 - h4)                              # w_turb (J/kg)

# ---- Fixed conditions (same as your study) ----
T1 = 35 + 273.15       # K
T3 = 150 + 273.15      # K
P_low = 80e5           # Pa
m_dot = 20.0           # kg/s

# Sweep high pressure
P_high_bar = np.arange(120, 301, 10)

W_turb_list = []
W_comp_list = []

for P_h in P_high_bar:
    P_high = P_h * 1e5

    # 1->2 compressor
    T2, h2, w_c = comp(T1, P_low, P_high)

    # 2->3 heater (set T3 at P_high)
    # (we don't need q_in for this plot)

    # 3->4 turbine
    T4, h4, w_t = turb(T3, P_high, P_low)

    # Convert specific work (J/kg) to power (MW)
    W_comp_list.append(m_dot * w_c / 1e6)
    W_turb_list.append(m_dot * w_t / 1e6)

# ---- Plot + Save (no plt.show to avoid GUI errors) ----
plt.figure()
plt.plot(P_high_bar, W_turb_list, label="Turbine Power (MW)")
plt.plot(P_high_bar, W_comp_list, label="Compressor Power (MW)")
plt.xlabel("High Pressure $P_{high}$ (bar)")
plt.ylabel("Power (MW)")
plt.title("Turbine and Compressor Power vs High Pressure")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("turbine_compressor_vs_phigh.png", dpi=300)
plt.close()

print("Saved: turbine_compressor_vs_phigh.png")
