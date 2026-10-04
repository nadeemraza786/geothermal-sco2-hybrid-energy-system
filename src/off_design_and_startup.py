import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cycle_model import run_cycle

def exp_ramp(t, tau, final_value):
    return final_value * (1.0 - np.exp(-t / tau))

def startup_simulation():
    t_s = np.arange(0, 3600 + 30, 30)
    rows = []

    for t in t_s:
        p_high = max(90.0, exp_ramp(t, 900.0, 160.0))
        T3_C = max(35.0, exp_ramp(t, 1200.0, 150.0))
        m_dot = min(20.0, exp_ramp(t, 600.0, 20.0))

        r = run_cycle(
            P_low_bar=85.0,
            P_high_bar=p_high,
            T3_C=T3_C,
            m_dot=m_dot,
            use_recuperator=True,
        )

        generating = (
            r["W_net_MW"] > 0.0
            and r["Q_in_MW"] > 0.0
            and np.isfinite(r["eta_th"])
        )

        rows.append({
            "time_min": t / 60.0,
            "P_high_bar": p_high,
            "T3_C": T3_C,
            "m_dot_kg_s": m_dot,
            "W_net_MW": r["W_net_MW"],
            "Q_in_MW": r["Q_in_MW"],
            "eta_th": r["eta_th"] if generating else np.nan,
            "generating": generating,
        })

    df = pd.DataFrame(rows)
    df.to_csv("data/startup_results.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(df["time_min"], df["W_net_MW"])
    ax.axhline(0.0, linewidth=1)
    ax.set_xlabel("Time, min")
    ax.set_ylabel("Net power, MW")
    ax.set_title("Quasi Steady Start Up Net Power")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig("figures/generated_startup_net_power.png", dpi=240)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(df["time_min"], 100*df["eta_th"])
    ax.set_xlabel("Time, min")
    ax.set_ylabel("Thermal efficiency, percent")
    ax.set_title("Quasi Steady Start Up Efficiency During Generating Operation")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig("figures/generated_startup_efficiency.png", dpi=240)
    plt.close(fig)

if __name__ == "__main__":
    startup_simulation()
