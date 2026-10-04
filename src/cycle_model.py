from CoolProp.CoolProp import PropsSI
from thermo_components import compressor, turbine, recuperator, FLUID

def run_cycle(
    P_low_bar=85.0,
    P_high_bar=160.0,
    T1_C=35.0,
    T3_C=150.0,
    m_dot=20.0,
    eta_c=0.80,
    eta_t=0.85,
    use_recuperator=True,
    eps=0.80,
):
    P_low = P_low_bar * 1e5
    P_high = P_high_bar * 1e5
    T1 = T1_C + 273.15
    T3 = T3_C + 273.15

    c = compressor(T1, P_low, P_high, eta_c)
    t = turbine(T3, P_high, P_low, eta_t)

    h_heater_in = c["h"]
    recup_active = False
    q_recup = 0.0

    if use_recuperator:
        r = recuperator(c["h"], c["T"], P_high, t["h"], t["T"], eps)
        h_heater_in = r["h2r"]
        recup_active = r["active"]
        q_recup = r["q_recup"]

    h3 = PropsSI("H", "T", T3, "P", P_high, FLUID)
    q_in = h3 - h_heater_in
    w_net = t["w"] - c["w"]

    W_net_MW = m_dot * w_net / 1e6
    Q_in_MW = m_dot * q_in / 1e6
    eta_th = W_net_MW / Q_in_MW if Q_in_MW > 0 else float("nan")

    return {
        "W_net_MW": W_net_MW,
        "Q_in_MW": Q_in_MW,
        "eta_th": eta_th,
        "T2_C": c["T"] - 273.15,
        "T4_C": t["T"] - 273.15,
        "recuperator_active": recup_active,
        "Q_recup_MW": m_dot * q_recup / 1e6,
        "pressure_ratio": P_high_bar / P_low_bar,
    }
