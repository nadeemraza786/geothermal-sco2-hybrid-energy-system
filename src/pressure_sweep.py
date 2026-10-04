import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cycle_model import run_cycle

P_LOW_BAR = 85.0
P_HIGH = np.arange(120.0, 301.0, 10.0)

rows = []
for p_high in P_HIGH:
    no_recup = run_cycle(P_low_bar=P_LOW_BAR, P_high_bar=p_high, use_recuperator=False)
    recup = run_cycle(P_low_bar=P_LOW_BAR, P_high_bar=p_high, use_recuperator=True)

    rows.append({
        "P_high_bar": p_high,
        "W_net_no_recup_MW": no_recup["W_net_MW"],
        "W_net_recup_MW": recup["W_net_MW"],
        "eta_no_recup": no_recup["eta_th"],
        "eta_recup": recup["eta_th"],
        "Qin_no_recup_MW": no_recup["Q_in_MW"],
        "Qin_recup_MW": recup["Q_in_MW"],
        "T2_C": recup["T2_C"],
        "T4_C": recup["T4_C"],
        "recuperator_active": recup["recuperator_active"],
    })

df = pd.DataFrame(rows)
df.to_csv("data/pressure_sweep_results.csv", index=False)

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(df["P_high_bar"], df["W_net_no_recup_MW"], label="No recuperator")
ax.plot(df["P_high_bar"], df["W_net_recup_MW"], label="With recuperator")
ax.set_xlabel("High pressure, bar")
ax.set_ylabel("Net power, MW")
ax.set_title("Net Power Sensitivity to High Pressure")
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig("figures/generated_net_power_pressure.png", dpi=240)
plt.close(fig)

fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(df["P_high_bar"], 100*df["eta_no_recup"], label="No recuperator")
ax.plot(df["P_high_bar"], 100*df["eta_recup"], label="With recuperator")
ax.set_xlabel("High pressure, bar")
ax.set_ylabel("Thermal efficiency, percent")
ax.set_title("Thermal Efficiency Sensitivity to High Pressure")
ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig("figures/generated_efficiency_pressure.png", dpi=240)
plt.close(fig)
