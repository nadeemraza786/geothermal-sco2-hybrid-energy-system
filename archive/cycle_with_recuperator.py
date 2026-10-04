# cycle_with_recuperator.py
# Adds a recuperator to your simple sCO2 Brayton (geothermal) cycle and compares:
# 1) Net Power vs P_high (with vs without recuperator)
# 2) Thermal Efficiency vs P_high (with vs without recuperator)
# 3) Heat Input Q_in vs P_high (with vs without recuperator)
#
# It also prints the optimal P_high for max net power (for both cases).
#
# Run:
#   python cycle_with_recuperator.py
#
# Output PNGs:
#   compare_net_power_vs_phigh.png
#   compare_efficiency_vs_phigh.png
#   compare_qin_vs_phigh.png

import numpy as np
import matplotlib.pyplot as plt
from CoolProp.CoolProp import PropsSI

FLUID = "CO2"

def comp(T1, P1, P2, eta_c=0.80):
    """Compressor: (T1,P1)->P2 with isentropic efficiency eta_c. Returns T2,h2,w_c."""
    h1 = PropsSI("H", "T", T1, "P", P1, FLUID)
    s1 = PropsSI("S", "T", T1, "P", P1, FLUID)
    h2s = PropsSI("H", "P", P2, "S", s1, FLUID)
    h2  = h1 + (h2s - h1) / eta_c
    T2  = PropsSI("T", "P", P2, "H", h2, FLUID)
    w_c = h2 - h1
    return T2, h2, w_c

def turb(T3, P3, P4, eta_t=0.85):
    """Turbine: (T3,P3)->P4 with isentropic efficiency eta_t. Returns T4,h4,w_t."""
    h3 = PropsSI("H", "T", T3, "P", P3, FLUID)
    s3 = PropsSI("S", "T", T3, "P", P3, FLUID)
    h4s = PropsSI("H", "P", P4, "S", s3, FLUID)
    h4  = h3 - eta_t * (h3 - h4s)
    T4  = PropsSI("T", "P", P4, "H", h4, FLUID)
    w_t = h3 - h4
    return T4, h4, w_t

def recuperator(h2, P_high, h4, T4, eps=0.80):
    """
    Simple effectiveness-based recuperator model.
    Cold side: state 2 (P_high, h2) -> 2r
    Hot side:  state 4 (P_low,  h4) -> 4r
    Assumes same m_dot both sides, no pressure drops.
    """
    # cold-side maximum: cold outlet temperature cannot exceed hot inlet temperature (T4)
    h2_max = PropsSI("H", "T", T4, "P", P_high, FLUID)

    # actual cold outlet enthalpy
    h2r = h2 + eps * (h2_max - h2)

    # energy balance: hot side loses same enthalpy the cold side gains
    h4r = h4 - (h2r - h2)

    return h2r, h4r

def run_cycle(P_high, P_low, T1, T3, m_dot, eta_c=0.80, eta_t=0.85, use_recup=False, eps=0.80):
    """
    Returns:
      W_net_MW, eta_th, Qin_MW, (T2_C, T4_C, T2r_C or None)
    """
    # 1->2 compressor
    T2, h2, w_c = comp(T1, P_low, P_high, eta_c=eta_c)

    # 3->4 turbine (we need T4 and h4 for recuperator)
    T4, h4, w_t = turb(T3, P_high, P_low, eta_t=eta_t)

    # If recuperator: preheat after compressor, reduce geothermal heat required
    if use_recup:
        h2r, h4r = recuperator(h2, P_high, h4, T4, eps=eps)
        # geothermal heater: 2r -> 3 (fixed T3 at P_high)
        h3 = PropsSI("H", "T", T3, "P", P_high, FLUID)
        q_in = h3 - h2r
        T2r = PropsSI("T", "P", P_high, "H", h2r, FLUID)
        T2r_C = T2r - 273.15
    else:
        # geothermal heater: 2 -> 3
        h3 = PropsSI("H", "T", T3, "P", P_high, FLUID)
        q_in = h3 - h2
        T2r_C = None

    # net specific work
    w_net = w_t - w_c

    # power & efficiency
    W_net_MW = m_dot * w_net / 1e6
    Qin_MW   = m_dot * q_in  / 1e6
    eta_th   = (W_net_MW / Qin_MW) if Qin_MW > 0 else np.nan

    T2_C = T2 - 273.15
    T4_C = T4 - 273.15

    return W_net_MW, eta_th, Qin_MW, (T2_C, T4_C, T2r_C)

def main():
    # ---- Your base assumptions (edit if needed) ----
    T1 = 35 + 273.15       # K
    T3 = 150 + 273.15      # K
    m_dot = 20.0           # kg/s

    # Use your optimized low pressure if you want (85 bar from your map),
    # or keep 80 bar if you prefer:
    P_low_bar = 85
    P_low = P_low_bar * 1e5

    # Sweep high pressure
    P_high_bar = np.arange(120, 301, 10)

    # Recuperator settings
    eps = 0.80

    # Store results
    W_no, eta_no, Qin_no = [], [], []
    W_re, eta_re, Qin_re = [], [], []

    for Ph in P_high_bar:
        P_high = Ph * 1e5

        # without recuperator
        Wn, etan, Qn, _ = run_cycle(
            P_high, P_low, T1, T3, m_dot, use_recup=False
        )
        W_no.append(Wn); eta_no.append(etan); Qin_no.append(Qn)

        # with recuperator
        Wr, etar, Qr, _ = run_cycle(
            P_high, P_low, T1, T3, m_dot, use_recup=True, eps=eps
        )
        W_re.append(Wr); eta_re.append(etar); Qin_re.append(Qr)

    W_no = np.array(W_no); eta_no = np.array(eta_no); Qin_no = np.array(Qin_no)
    W_re = np.array(W_re); eta_re = np.array(eta_re); Qin_re = np.array(Qin_re)

    # ---- Print best P_high for max net power ----
    i_no = int(np.nanargmax(W_no))
    i_re = int(np.nanargmax(W_re))

    print("\n=== WITHOUT recuperator ===")
    print("Best P_high (bar):", int(P_high_bar[i_no]))
    print("Max Net Power (MW):", round(float(W_no[i_no]), 3))
    print("Efficiency at best:", round(float(eta_no[i_no]), 3))
    print("Q_in at best (MW):", round(float(Qin_no[i_no]), 3))

    print("\n=== WITH recuperator (eps = {:.2f}) ===".format(eps))
    print("Best P_high (bar):", int(P_high_bar[i_re]))
    print("Max Net Power (MW):", round(float(W_re[i_re]), 3))
    print("Efficiency at best:", round(float(eta_re[i_re]), 3))
    print("Q_in at best (MW):", round(float(Qin_re[i_re]), 3))

    # ---- Plots (save + close; no plt.show) ----

    # 1) Net Power comparison
    plt.figure()
    plt.plot(P_high_bar, W_no, label="No recuperator")
    plt.plot(P_high_bar, W_re, label=f"With recuperator (eps={eps:.2f})")
    plt.xlabel("High Pressure $P_{high}$ (bar)")
    plt.ylabel("Net Power (MW)")
    plt.title(f"Net Power vs High Pressure (P_low={P_low_bar} bar, T3=150°C)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("compare_net_power_vs_phigh.png", dpi=300)
    plt.close()
    print("Saved: compare_net_power_vs_phigh.png")

    # 2) Efficiency comparison
    plt.figure()
    plt.plot(P_high_bar, eta_no, label="No recuperator")
    plt.plot(P_high_bar, eta_re, label=f"With recuperator (eps={eps:.2f})")
    plt.xlabel("High Pressure $P_{high}$ (bar)")
    plt.ylabel("Thermal Efficiency (-)")
    plt.title(f"Thermal Efficiency vs High Pressure (P_low={P_low_bar} bar, T3=150°C)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("compare_efficiency_vs_phigh.png", dpi=300)
    plt.close()
    print("Saved: compare_efficiency_vs_phigh.png")

    # 3) Heat input comparison
    plt.figure()
    plt.plot(P_high_bar, Qin_no, label="No recuperator")
    plt.plot(P_high_bar, Qin_re, label=f"With recuperator (eps={eps:.2f})")
    plt.xlabel("High Pressure $P_{high}$ (bar)")
    plt.ylabel("Geothermal Heat Input $Q_{in}$ (MW)")
    plt.title(f"Geothermal Heat Input vs High Pressure (P_low={P_low_bar} bar, T3=150°C)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("compare_qin_vs_phigh.png", dpi=300)
    plt.close()
    print("Saved: compare_qin_vs_phigh.png")

if __name__ == "__main__":
    main()
