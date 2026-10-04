import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

def comp(T1, P1, P2, eta=0.80):
    h1 = PropsSI("H", "T", T1, "P", P1, FLUID)
    s1 = PropsSI("S", "T", T1, "P", P1, FLUID)
    h2s = PropsSI("H", "P", P2, "S", s1, FLUID)
    h2  = h1 + (h2s - h1) / eta
    return h2, (h2 - h1)  # h2, w_comp (J/kg)

def turb(T3, P3, P4, eta=0.85):
    h3 = PropsSI("H", "T", T3, "P", P3, FLUID)
    s3 = PropsSI("S", "T", T3, "P", P3, FLUID)
    h4s = PropsSI("H", "P", P4, "S", s3, FLUID)
    h4  = h3 - eta * (h3 - h4s)
    return h3, h4, (h3 - h4)  # h3, h4, w_turb (J/kg)

# Fixed temperatures
T1 = 35 + 273.15
T3 = 150 + 273.15

# Choose ranges (bar)
P_low_bar  = np.arange(75, 101, 5)      # 75..100 bar
P_high_bar = np.arange(120, 301, 10)    # 120..300 bar

m_dot = 20.0  # keep same as before (MW scaling)

Wnet_MW = np.full((len(P_low_bar), len(P_high_bar)), np.nan)

# Grid search
for i, Pl in enumerate(P_low_bar):
    P_low = Pl * 1e5
    for j, Ph in enumerate(P_high_bar):
        if Ph <= Pl:
            continue  # must have P_high > P_low
        P_high = Ph * 1e5

        # Compressor and turbine
        h2, w_c = comp(T1, P_low, P_high)
        h3, h4, w_t = turb(T3, P_high, P_low)

        w_net = w_t - w_c
        Wnet_MW[i, j] = m_dot * w_net / 1e6  # MW

# Find best point
best_idx = np.nanargmax(Wnet_MW)
best_i, best_j = np.unravel_index(best_idx, Wnet_MW.shape)

best_Plow  = P_low_bar[best_i]
best_Phigh = P_high_bar[best_j]
best_Wnet  = Wnet_MW[best_i, best_j]

print("Best P_low (bar):", best_Plow)
print("Best P_high (bar):", best_Phigh)
print("Max Net Power (MW):", round(best_Wnet, 3))

# Optional: save a heatmap (nice for thesis)
plt.figure()
plt.imshow(
    Wnet_MW,
    origin="lower",
    aspect="auto",
    extent=[P_high_bar[0], P_high_bar[-1], P_low_bar[0], P_low_bar[-1]]
)
plt.xlabel("High Pressure P_high (bar)")
plt.ylabel("Low Pressure P_low (bar)")
plt.title("Net Power (MW) map")
plt.colorbar(label="Net Power (MW)")
plt.scatter(best_Phigh, best_Plow, marker="x")
plt.tight_layout()
plt.savefig("net_power_map_plow_phigh.png", dpi=300)
plt.close()

print("Saved: net_power_map_plow_phigh.png")
