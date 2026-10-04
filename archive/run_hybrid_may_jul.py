import pandas as pd
import matplotlib.pyplot as plt
from hybrid_dispatch import simulate_hybrid

def main():
    df = pd.read_csv("data/nuernberg_pv_may_jul_hourly.csv", index_col=0, parse_dates=True)

    # --- Choose your geothermal baseline from your sCO2 model ---
    # Example: 0.25 MW (you can replace with your computed best net power)
    P_geo_MW = 0.25

    # Battery sizing (start with something moderate)
    E_batt_MWh = 2.0
    P_batt_max_MW = 0.5

    out = simulate_hybrid(
        df,
        P_geo_MW=P_geo_MW,
        E_batt_MWh=E_batt_MWh,
        P_batt_max_MW=P_batt_max_MW,
        eta_c=0.95,
        eta_d=0.95,
        soc0=0.50
    )

    # Key results
    pv_mwh = out["P_pv_MW"].sum() * 1.0
    grid_mwh = out["P_grid_MW"].sum() * 1.0
    curt_mwh = out["P_curt_MW"].sum() * 1.0

    print(f"PV energy (May–Jul): {pv_mwh:.2f} MWh")
    print(f"Energy to grid (May–Jul): {grid_mwh:.2f} MWh")
    print(f"PV curtailed (May–Jul): {curt_mwh:.2f} MWh")
    print(f"Final SOC: {out['SOC'].iloc[-1]:.3f}")

    # Plot first week only (clean)
    week = out.iloc[:24*7]

    plt.figure()
    plt.plot(week.index, week["P_pv_MW"], label="PV (MW)")
    plt.plot(week.index, week["P_grid_MW"], label="Grid export (MW)")
    plt.ylabel("Power (MW)")
    plt.title("Hybrid: PV and Grid Power (first week)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("hybrid_first_week_power.png", dpi=200)
    plt.close()

    plt.figure()
    plt.plot(week.index, week["SOC"])
    plt.ylabel("SOC (-)")
    plt.title("Battery SOC (first week)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("hybrid_first_week_soc.png", dpi=200)
    plt.close()

    plt.figure()
    daily_curt = out["P_curt_MW"].resample("D").sum()
    plt.plot(daily_curt.index, daily_curt.values)
    plt.ylabel("Curtailment (MWh/day)")
    plt.title("Daily PV Curtailment (May–Jul)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("hybrid_daily_curtailment.png", dpi=200)
    plt.close()

    print("Saved plots in hybrid/:")
    print(" - hybrid_first_week_power.png")
    print(" - hybrid_first_week_soc.png")
    print(" - hybrid_daily_curtailment.png")

if __name__ == "__main__":
    main()
