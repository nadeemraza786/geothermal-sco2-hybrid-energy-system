import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

# ---------------- Component models (same as your steady model) ----------------
def compressor(T1, P1, P2, eta=0.80):
    h1 = PropsSI("H","T",T1,"P",P1,FLUID)
    s1 = PropsSI("S","T",T1,"P",P1,FLUID)
    h2s = PropsSI("H","P",P2,"S",s1,FLUID)
    h2  = h1 + (h2s - h1)/eta
    T2  = PropsSI("T","P",P2,"H",h2,FLUID)
    w_c = h2 - h1
    return T2, h2, w_c

def turbine(T3, P3, P4, eta=0.85):
    h3 = PropsSI("H","T",T3,"P",P3,FLUID)
    s3 = PropsSI("S","T",T3,"P",P3,FLUID)
    h4s = PropsSI("H","P",P4,"S",s3,FLUID)
    h4  = h3 - eta*(h3 - h4s)
    T4  = PropsSI("T","P",P4,"H",h4,FLUID)
    w_t = h3 - h4
    return T4, h4, w_t, h3

def recuperator_simple(h2, P_high, h4, T4, eps=0.80):
    # cold outlet cannot exceed hot inlet temperature
    h2_max = PropsSI("H","T",T4,"P",P_high,FLUID)
    h2r = h2 + eps*(h2_max - h2)
    h4r = h4 - (h2r - h2)
    return h2r, h4r

def run_cycle(P_low, P_high, T1, T3, m_dot,
              eta_c=0.80, eta_t=0.85,
              use_recup=True, eps=0.80):
    """
    Returns: W_net_MW, Qin_MW, eta_th, T2_C, T4_C
    """
    # compressor
    T2, h2, w_c = compressor(T1, P_low, P_high, eta=eta_c)

    # turbine
    T4, h4, w_t, h3 = turbine(T3, P_high, P_low, eta=eta_t)

    # recuperator (optional)
    if use_recup:
        h2r, h4r = recuperator_simple(h2, P_high, h4, T4, eps=eps)
        q_in = h3 - h2r
    else:
        q_in = h3 - h2

    w_net = w_t - w_c

    W_net_MW = m_dot * w_net / 1e6
    Qin_MW   = m_dot * q_in  / 1e6
    eta_th   = (W_net_MW / Qin_MW) if Qin_MW > 1e-9 else np.nan

    return W_net_MW, Qin_MW, eta_th, (T2 - 273.15), (T4 - 273.15)

# ---------------- RAMP functions (start-up logic) ----------------
def exp_ramp(t, tau, x_final):
    """Smooth exponential ramp: starts at 0 and approaches x_final."""
    return x_final * (1 - np.exp(-t / tau))

def clamp(x, x_min, x_max):
    return max(x_min, min(x, x_max))

# ---------------- Main unsteady simulation ----------------
def main():
    # Fixed (cold start) inlet and low pressure
    T1 = 35 + 273.15
    P_low_bar = 85
    P_low = P_low_bar * 1e5

    # Final (steady) targets
    P_high_final_bar = 160
    T3_final_C = 150
    m_dot_final = 20.0

    # Start-up time settings
    t_end = 3600          # seconds (1 hour)
    dt = 30               # seconds
    t = np.arange(0, t_end + dt, dt)

    # Time constants (how fast you ramp each variable)
    tau_P = 900           # pressure builds in ~15 min
    tau_T = 1200          # temperature rises in ~20 min
    tau_m = 600           # mass flow rises in ~10 min

    # Storage
    P_high_bar_list = []
    T3_C_list = []
    m_dot_list = []
    Wnet_list = []
    Qin_list = []
    eta_list = []

    # Choose whether to include recuperator in start-up simulation
    use_recup = True
    eps = 0.80

    for ti in t:
        # ramp variables (smoothly)
        P_high_bar = exp_ramp(ti, tau_P, P_high_final_bar)
        T3_C = exp_ramp(ti, tau_T, T3_final_C)
        m_dot = exp_ramp(ti, tau_m, m_dot_final)

        # enforce realistic limits
        P_high_bar = clamp(P_high_bar, P_low_bar + 5, 300)  # keep > P_low
        T3_C = clamp(T3_C, 35, T3_final_C)
        m_dot = clamp(m_dot, 0.0, m_dot_final)

        P_high = P_high_bar * 1e5
        T3 = T3_C + 273.15

        # Run your steady cycle at this time step (quasi-steady)
        Wnet, Qin, eta_th, T2C, T4C = run_cycle(
            P_low=P_low,
            P_high=P_high,
            T1=T1,
            T3=T3,
            m_dot=m_dot,
            use_recup=use_recup,
            eps=eps
        )

        # store
        P_high_bar_list.append(P_high_bar)
        T3_C_list.append(T3_C)
        m_dot_list.append(m_dot)
        Wnet_list.append(Wnet)
        Qin_list.append(Qin)
        eta_list.append(eta_th)

    # Convert to arrays
    P_high_bar_list = np.array(P_high_bar_list)
    T3_C_list = np.array(T3_C_list)
    m_dot_list = np.array(m_dot_list)
    Wnet_list = np.array(Wnet_list)
    Qin_list = np.array(Qin_list)
    eta_list = np.array(eta_list)

    # ---------------- Plots ----------------
    # 1) Inputs: P_high, T3, m_dot vs time
    plt.figure()
    plt.plot(t/60, P_high_bar_list)
    plt.xlabel("Time (min)")
    plt.ylabel("P_high (bar)")
    plt.title("Start-up Ramp: High Pressure")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("startup_phigh_vs_time.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(t/60, T3_C_list)
    plt.xlabel("Time (min)")
    plt.ylabel("T3 (°C)")
    plt.title("Start-up Ramp: Turbine Inlet Temperature")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("startup_T3_vs_time.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(t/60, m_dot_list)
    plt.xlabel("Time (min)")
    plt.ylabel("m_dot (kg/s)")
    plt.title("Start-up Ramp: Mass Flow Rate")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("startup_mdot_vs_time.png", dpi=300)
    plt.close()

    # 2) Outputs: Wnet, Qin, eta vs time
    plt.figure()
    plt.plot(t/60, Wnet_list)
    plt.xlabel("Time (min)")
    plt.ylabel("Net Power (MW)")
    plt.title("Start-up Response: Net Power vs Time")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("startup_net_power_vs_time.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(t/60, Qin_list)
    plt.xlabel("Time (min)")
    plt.ylabel("Geothermal Heat Input Qin (MW)")
    plt.title("Start-up Response: Heat Input vs Time")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("startup_qin_vs_time.png", dpi=300)
    plt.close()

    plt.figure()
    plt.plot(t/60, eta_list*100)
    plt.xlabel("Time (min)")
    plt.ylabel("Thermal Efficiency (%)")
    plt.title("Start-up Response: Thermal Efficiency vs Time")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("startup_efficiency_vs_time.png", dpi=300)
    plt.close()

    print("Saved start-up plots:")
    print("startup_phigh_vs_time.png")
    print("startup_T3_vs_time.png")
    print("startup_mdot_vs_time.png")
    print("startup_net_power_vs_time.png")
    print("startup_qin_vs_time.png")
    print("startup_efficiency_vs_time.png")

if __name__ == "__main__":
    main()
