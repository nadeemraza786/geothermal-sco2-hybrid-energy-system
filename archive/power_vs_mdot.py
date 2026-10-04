import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

def comp(T1, P1, P2, eta=0.80):
    h1 = PropsSI("H","T",T1,"P",P1,FLUID)
    s1 = PropsSI("S","T",T1,"P",P1,FLUID)
    h2s = PropsSI("H","P",P2,"S",s1,FLUID)
    h2  = h1 + (h2s - h1)/eta
    return h2, (h2 - h1)

def turb(T3, P3, P4, eta=0.85):
    h3 = PropsSI("H","T",T3,"P",P3,FLUID)
    s3 = PropsSI("S","T",T3,"P",P3,FLUID)
    h4s = PropsSI("H","P",P4,"S",s3,FLUID)
    h4  = h3 - eta*(h3 - h4s)
    return h3, h4, (h3 - h4)

# Fixed optimum pressures from your results
P_low = 80e5
P_high = 160e5
T1 = 35 + 273.15
T3 = 150 + 273.15

m_dot_list = np.arange(5, 61, 5)  # 5 to 60 kg/s
W_net_list = []

for m_dot in m_dot_list:
    h2, w_c = comp(T1, P_low, P_high)
    h3, h4, w_t = turb(T3, P_high, P_low)

    w_net = w_t - w_c
    W_net_list.append(m_dot * w_net / 1e6)

plt.figure()
plt.plot(m_dot_list, W_net_list)
plt.xlabel("Mass flow rate m_dot (kg/s)")
plt.ylabel("Net Power (MW)")
plt.title("Net Power vs Mass Flow Rate (at P_high=160 bar)")
plt.grid(True)
plt.tight_layout()
plt.savefig("net_power_vs_mdot.png", dpi=300)
plt.close()

print("Saved: net_power_vs_mdot.png")
