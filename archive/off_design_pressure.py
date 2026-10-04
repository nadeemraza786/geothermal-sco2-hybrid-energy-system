import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

# ---------- compressor ----------
def comp(T1, P1, P2, eta=0.80):
    h1 = PropsSI("H","T",T1,"P",P1,FLUID)
    s1 = PropsSI("S","T",T1,"P",P1,FLUID)
    h2s = PropsSI("H","P",P2,"S",s1,FLUID)
    h2  = h1 + (h2s - h1)/eta
    T2  = PropsSI("T","P",P2,"H",h2,FLUID)
    return T2, h2, (h2 - h1)

# ---------- turbine ----------
def turb(T3, P3, P4, eta=0.85):
    h3 = PropsSI("H","T",T3,"P",P3,FLUID)
    s3 = PropsSI("S","T",T3,"P",P3,FLUID)
    h4s = PropsSI("H","P",P4,"S",s3,FLUID)
    h4  = h3 - eta*(h3 - h4s)
    T4  = PropsSI("T","P",P4,"H",h4,FLUID)
    return T4, h4, (h3 - h4)

# ---------- fixed conditions ----------
T1 = 35 + 273.15          # compressor inlet temperature (K)
T3 = 150 + 273.15         # geothermal temperature (K)
P_low = 80e5              # low pressure (Pa)
m_dot = 20.0              # mass flow rate (kg/s)

# ---------- pressure sweep ----------
P_high_bar = np.arange(120, 301, 10)   # 120 to 300 bar
W_net_list = []

for P_h in P_high_bar:
    P_high = P_h * 1e5

    # Compressor
    T2, h2, w_c = comp(T1, P_low, P_high)

    # Heater
    h3 = PropsSI("H","T",T3,"P",P_high,FLUID)
    q_in = h3 - h2

    # Turbine
    T4, h4, w_t = turb(T3, P_high, P_low)

    # Net power
    w_net = w_t - w_c
    W_net_list.append(m_dot * w_net / 1e6)

# ---------- plot ----------
plt.figure()
plt.plot(P_high_bar, W_net_list)
plt.xlabel("High Pressure P_high (bar)")
plt.ylabel("Net Power (MW)")
plt.title("Net Power vs High Pressure")
plt.grid(True)
plt.savefig("net_power_vs_pressure.png", dpi=300)
plt.close()
import numpy as np

# Convert list to array
W_net_arr = np.array(W_net_list)

# Find index of maximum net power
best_index = np.argmax(W_net_arr)

# Print optimal results
print("Optimal High Pressure (bar):", P_high_bar[best_index])
print("Maximum Net Power (MW):", round(W_net_arr[best_index], 3))

