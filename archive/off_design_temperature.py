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

# ---------- off-design study ----------
T1 = 35 + 273.15
P_low  = 80e5
P_high = 200e5
m_dot = 20.0

T3_range_C = np.arange(120, 181, 5)

W_net_list = []
eta_list   = []
W_turb_list = []
W_comp_list = []

for T3_C in T3_range_C:
    T3 = T3_C + 273.15

    # Compressor
    T2, h2, w_c = comp(T1, P_low, P_high)

    # Heater
    h3 = PropsSI("H","T",T3,"P",P_high,FLUID)
    q_in = h3 - h2

    # Turbine
    T4, h4, w_t = turb(T3, P_high, P_low)

    # Results
    w_net = w_t - w_c
    eta = w_net / q_in

    W_net_list.append(m_dot * w_net / 1e6)
    eta_list.append(eta)
    W_turb_list.append(m_dot * w_t / 1e6)
    W_comp_list.append(m_dot * w_c / 1e6)

# ---------- PLOTS ----------

# 1) Net Power vs Geothermal Temperature
plt.figure()
plt.plot(T3_range_C, W_net_list)
plt.xlabel("Geothermal / Turbine Inlet Temperature (°C)")
plt.ylabel("Net Power (MW)")
plt.title("Net Power vs Geothermal Temperature")
plt.grid(True)
plt.show()

# 2) Efficiency vs Geothermal Temperature
plt.figure()
plt.plot(T3_range_C, eta_list)
plt.xlabel("Geothermal / Turbine Inlet Temperature (°C)")
plt.ylabel("Thermal Efficiency (-)")
plt.title("Efficiency vs Geothermal Temperature")
plt.grid(True)
plt.show()

# 3) Turbine & Compressor Power vs Geothermal Temperature
plt.figure()
plt.plot(T3_range_C, W_turb_list, label="Turbine Power")
plt.plot(T3_range_C, W_comp_list, label="Compressor Power")
plt.xlabel("Geothermal / Turbine Inlet Temperature (°C)")
plt.ylabel("Power (MW)")
plt.title("Turbine and Compressor Power vs Temperature")
plt.legend()
plt.grid(True)
plt.savefig("net_power_vs_pressure.png", dpi=300)
plt.close()

