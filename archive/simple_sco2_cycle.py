from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

def comp(T1, P1, P2, eta=0.80):
    h1 = PropsSI("H","T",T1,"P",P1,FLUID)
    s1 = PropsSI("S","T",T1,"P",P1,FLUID)
    h2s = PropsSI("H","P",P2,"S",s1,FLUID)      # isentropic
    h2  = h1 + (h2s - h1)/eta                   # real
    T2  = PropsSI("T","P",P2,"H",h2,FLUID)
    return T2, h2, (h2 - h1)                    # specific work (J/kg)

def turb(T3, P3, P4, eta=0.85):
    h3 = PropsSI("H","T",T3,"P",P3,FLUID)
    s3 = PropsSI("S","T",T3,"P",P3,FLUID)
    h4s = PropsSI("H","P",P4,"S",s3,FLUID)      # isentropic
    h4  = h3 - eta*(h3 - h4s)                   # real
    T4  = PropsSI("T","P",P4,"H",h4,FLUID)
    return T4, h4, (h3 - h4)                    # specific work out (J/kg)

def run():
    # ---- inputs (change later) ----
    T1 = 35 + 273.15        # cooler outlet / compressor inlet (K)
    T3 = 150 + 273.15       # geothermal heater outlet / turbine inlet (K)
    P_low  = 80e5           # 80 bar
    P_high = 200e5          # 200 bar
    m_dot = 20.0            # kg/s

    # 1->2 compressor
    T2, h2, w_c = comp(T1, P_low, P_high)

    # 2->3 heater (set T3)
    h3 = PropsSI("H","T",T3,"P",P_high,FLUID)
    q_in = h3 - h2

    # 3->4 turbine
    T4, h4, w_t = turb(T3, P_high, P_low)

    # results
    w_net = w_t - w_c
    eta_th = w_net / q_in

    W_net_MW = m_dot * w_net / 1e6
    print("Net Power (MW):", round(W_net_MW, 2))
    print("Thermal efficiency:", round(eta_th, 3))
    print("State T (°C): T1=", round(T1-273.15,1),
          "T2=", round(T2-273.15,1),
          "T3=", round(T3-273.15,1),
          "T4=", round(T4-273.15,1))

if __name__ == "__main__":
    run()
