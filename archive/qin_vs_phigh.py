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
    return T2, h2

# ---- Fixed conditions (same as your study) ----
T1 = 35 + 273.15        # K (compressor inlet)
T3 = 150 + 273.15       # K (turbine inlet set by geothermal)
P_low = 80e5            # Pa
m_dot = 20.0            # kg/s

# ---- Sweep high pressure ----
P_high_bar = np.arange(120, 301, 10)
Qin_list_MW = []
qin_list_kJkg = []

for P_h in P_high_bar:
    P_high = P_h * 1e5

    # 1->2 compressor
    T2, h2 = comp(T1, P_low, P_high)

    # 2->3 geothermal heating at fixed T3
    h3 = PropsSI("H", "T", T3, "P", P_high, FLUID)

    # Heat input per kg
    q_in = h3 - h2               # J/kg
    qin_list_kJkg.append(q_in / 1000)

    # Heat input rate (power) in MW
    Qin_list_MW.append(m_dot * q_in / 1e6)

# ---- Plot (save + close) ----
plt.figure()
plt.plot(P_high_bar, Qin_list_MW)
plt.xlabel("High Pressure $P_{high}$ (bar)")
plt.ylabel("Heat Input $Q_{in}$ (MW)")
plt.title("Geothermal Heat Input vs High Pressure")
plt.grid(True)
plt.tight_layout()
plt.savefig("qin_vs_phigh.png", dpi=300)
plt.close()

print("Saved: qin_vs_phigh.png")
