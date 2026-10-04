import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

# -------- Component models --------
def compressor(T1, P1, P2, eta=0.80):
    h1 = PropsSI("H","T",T1,"P",P1,FLUID)
    s1 = PropsSI("S","T",T1,"P",P1,FLUID)
    h2s = PropsSI("H","P",P2,"S",s1,FLUID)
    h2  = h1 + (h2s - h1)/eta
    return h2, (h2 - h1)

def turbine(T3, P3, P4, eta=0.85):
    h3 = PropsSI("H","T",T3,"P",P3,FLUID)
    s3 = PropsSI("S","T",T3,"P",P3,FLUID)
    h4s = PropsSI("H","P",P4,"S",s3,FLUID)
    h4  = h3 - eta*(h3 - h4s)
    return h3, h4, (h3 - h4)

def recuperator(h2, P_high, h4, T4, eps=0.8):
    h2_max = PropsSI("H","T",T4,"P",P_high,FLUID)
    h2r = h2 + eps*(h2_max - h2)
    h4r = h4 - (h2r - h2)
    return h2r, h4r

# -------- Fixed conditions --------
T1 = 35 + 273.15
T3 = 150 + 273.15
m_dot = 20.0
eps = 0.8

# Pressure ranges (bar)
P_low_bar  = np.arange(75, 101, 5)
P_high_bar = np.arange(120, 301, 10)

# Result storage
Wnet = np.zeros((len(P_low_bar), len(P_high_bar)))
eta  = np.zeros_like(Wnet)

# -------- Main sweep --------
for i, Pl in enumerate(P_low_bar):
    for j, Ph in enumerate(P_high_bar):
        if Ph <= Pl:
            Wnet[i,j] = np.nan
            eta[i,j]  = np.nan
            continue

        P_low  = Pl*1e5
        P_high = Ph*1e5

        # Compressor
        h2, w_c = compressor(T1, P_low, P_high)

        # Turbine
        h3, h4, w_t = turbine(T3, P_high, P_low)
        T4 = PropsSI("T","P",P_low,"H",h4,FLUID)

        # Recuperator
        h2r, h4r = recuperator(h2, P_high, h4, T4, eps)

        # Geothermal heat
        h3 = PropsSI("H","T",T3,"P",P_high,FLUID)
        q_in = h3 - h2r

        w_net = w_t - w_c
        Wnet[i,j] = m_dot*w_net/1e6
        eta[i,j]  = w_net/q_in

# -------- Find optimum --------
idx = np.nanargmax(Wnet)
i_opt, j_opt = np.unravel_index(idx, Wnet.shape)

Pl_opt = P_low_bar[i_opt]
Ph_opt = P_high_bar[j_opt]
Wopt  = Wnet[i_opt, j_opt]
etaopt = eta[i_opt, j_opt]

print("Optimal (with recuperator):")
print("P_low  =", Pl_opt, "bar")
print("P_high =", Ph_opt, "bar")
print("Net Power =", round(Wopt,3), "MW")
print("Efficiency =", round(etaopt*100,2), "%")

# -------- Plot 1: Net Power Map --------
plt.figure()
plt.contourf(P_high_bar, P_low_bar, Wnet, levels=20)
plt.colorbar(label="Net Power (MW)")
plt.scatter(Ph_opt, Pl_opt, color="red", marker="x", s=80)
plt.xlabel("High Pressure P_high (bar)")
plt.ylabel("Low Pressure P_low (bar)")
plt.title("Net Power Map (With Recuperator)")
plt.tight_layout()
plt.savefig("net_power_map_recuperator.png", dpi=300)
plt.close()

# -------- Plot 2: Efficiency Map --------
plt.figure()
plt.contourf(P_high_bar, P_low_bar, eta*100, levels=20)
plt.colorbar(label="Thermal Efficiency (%)")
plt.scatter(Ph_opt, Pl_opt, color="red", marker="x", s=80)
plt.xlabel("High Pressure P_high (bar)")
plt.ylabel("Low Pressure P_low (bar)")
plt.title("Thermal Efficiency Map (With Recuperator)")
plt.tight_layout()
plt.savefig("efficiency_map_recuperator.png", dpi=300)
plt.close()

print("Saved:")
print("net_power_map_recuperator.png")
print("efficiency_map_recuperator.png")
