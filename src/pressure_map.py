import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cycle_model import run_cycle

P_LOW = np.arange(75.0, 101.0, 5.0)
P_HIGH = np.arange(120.0, 301.0, 10.0)

rows = []
for p_low in P_LOW:
    for p_high in P_HIGH:
        if p_high <= p_low:
            continue
        r = run_cycle(P_low_bar=p_low, P_high_bar=p_high, use_recuperator=True)
        rows.append({
            "P_low_bar": p_low,
            "P_high_bar": p_high,
            "W_net_MW": r["W_net_MW"],
            "eta_th": r["eta_th"],
            "Q_in_MW": r["Q_in_MW"],
            "recuperator_active": r["recuperator_active"],
        })

df = pd.DataFrame(rows)
df.to_csv("data/pressure_map_results.csv", index=False)

best_power = df.loc[df["W_net_MW"].idxmax()]
best_eta = df.loc[df["eta_th"].idxmax()]

print("Best net power point")
print(best_power)
print("\nBest efficiency point")
print(best_eta)

for value, title, filename in [
    ("W_net_MW", "Net Power Map", "figures/generated_net_power_map.png"),
    ("eta_th", "Thermal Efficiency Map", "figures/generated_efficiency_map.png"),
]:
    pivot = df.pivot(index="P_low_bar", columns="P_high_bar", values=value)
    fig, ax = plt.subplots(figsize=(9, 6))
    c = ax.contourf(pivot.columns, pivot.index, pivot.values, levels=20)
    fig.colorbar(c, ax=ax, label=value)
    ax.set_xlabel("High pressure, bar")
    ax.set_ylabel("Low pressure, bar")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(filename, dpi=240)
    plt.close(fig)
