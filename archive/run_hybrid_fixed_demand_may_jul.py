import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # ✅ ADD THIS
import os

# -----------------------------
# INPUTS
# -----------------------------
CSV_PATH = "data/nuernberg_pv_2023_hourly.csv"

# Geothermal net power (MW) - constant baseload
P_GEO = 0.24

# Fixed demand profile (MW)
P_LOAD_CONST = 0.30

# Battery (trial)
E_BATT_MAX = 8.0   # MWh
P_BATT_MAX = 0.2   # MW
ETA_CH = 0.95
ETA_DIS = 0.95
SOC0 = 0.50

OUT_DIR = "hybrid"
os.makedirs(OUT_DIR, exist_ok=True)

# ✅ Helper: format x-axis as month names (Jan–Dec 2023)
def format_month_axis(ax):
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  # Jan, Feb, ...
    ax.set_xlabel("Month (2023)")

def main():
    df = pd.read_csv(CSV_PATH, index_col=0, parse_dates=True)

    if "P_pv_MW" not in df.columns:
        raise ValueError(f"'P_pv_MW' column not found. Columns: {list(df.columns)}")

    # ✅ Auto-detect timestep (hours)
    dt_h = df.index.to_series().diff().median().total_seconds() / 3600.0
    print("Detected dt_h (hours):", dt_h)
    print("Avg points per day:", df["P_pv_MW"].resample("D").count().mean())

    # Fixed load
    df["P_load_MW"] = P_LOAD_CONST

    n = len(df)
    soc = np.zeros(n)

    p_geo_used = np.zeros(n)
    p_pv_used = np.zeros(n)
    p_batt_to_load = np.zeros(n)
    p_batt_charge = np.zeros(n)
    p_curt = np.zeros(n)
    p_grid_import = np.zeros(n)
    p_to_load = np.zeros(n)

    # Battery energy (MWh)
    E = SOC0 * E_BATT_MAX

    for i, (_, row) in enumerate(df.iterrows()):
        P_pv = float(row["P_pv_MW"])
        P_load = float(row["P_load_MW"])

        # 1) Geothermal to load
        geo_used = min(P_GEO, P_load)
        remaining_load = P_load - geo_used

        # 2) PV to load
        pv_used = min(P_pv, remaining_load)
        remaining_load -= pv_used
        pv_left = P_pv - pv_used

        # 3) Charge battery with PV leftover
        charge_power = 0.0
        if pv_left > 0:
            charge_power = min(pv_left, P_BATT_MAX)

            # capacity limit
            E_can_add = (E_BATT_MAX - E)  # MWh
            charge_limit_by_energy = (E_can_add / dt_h) / ETA_CH  # MW
            charge_power = min(charge_power, charge_limit_by_energy)
            charge_power = max(charge_power, 0.0)

            E += charge_power * dt_h * ETA_CH

        curtailed = max(0.0, pv_left - charge_power)

        # 4) Discharge battery to remaining load
        discharge_power = 0.0
        if remaining_load > 0:
            discharge_power = min(remaining_load, P_BATT_MAX)

            # available energy limit
            E_can_take = E  # MWh
            discharge_limit_by_energy = (E_can_take / dt_h) * ETA_DIS  # MW deliverable
            discharge_power = min(discharge_power, discharge_limit_by_energy)
            discharge_power = max(discharge_power, 0.0)

            E -= (discharge_power * dt_h) / ETA_DIS
            remaining_load -= discharge_power

        # 5) Grid import
        grid_import = max(0.0, remaining_load)

        # Save
        p_geo_used[i] = geo_used
        p_pv_used[i] = pv_used
        p_batt_to_load[i] = discharge_power
        p_batt_charge[i] = charge_power
        p_curt[i] = curtailed
        p_grid_import[i] = grid_import
        p_to_load[i] = geo_used + pv_used + discharge_power
        soc[i] = E / E_BATT_MAX

    # -----------------------------
    # Summary metrics
    # -----------------------------
    E_load = df["P_load_MW"].sum() * dt_h
    E_served = p_to_load.sum() * dt_h
    E_import = p_grid_import.sum() * dt_h
    E_curt = p_curt.sum() * dt_h
    E_pv = df["P_pv_MW"].sum() * dt_h
    E_geo_used = p_geo_used.sum() * dt_h

    renewable_served = (p_geo_used + p_pv_used + p_batt_to_load).sum() * dt_h
    renewable_fraction = renewable_served / E_load if E_load > 0 else 0.0

    print("\n=== Hybrid results (FULL YEAR 2023) ===")
    print(f"Geothermal (constant): {P_GEO:.2f} MW")
    print(f"Fixed Load:            {P_LOAD_CONST:.2f} MW")
    print(f"Battery:               {E_BATT_MAX:.2f} MWh, {P_BATT_MAX:.2f} MW")
    print("--------------------------------")
    print(f"Total Load Energy:     {E_load:.2f} MWh")
    print(f"Energy Served:         {E_served:.2f} MWh")
    print(f"Grid Import Needed:    {E_import:.2f} MWh")
    print(f"PV Energy Produced:    {E_pv:.2f} MWh")
    print(f"PV Curtailed:          {E_curt:.2f} MWh")
    print(f"Geo Used Energy:       {E_geo_used:.2f} MWh")
    print(f"Renewable fraction:    {renewable_fraction*100:.1f} %")
    print(f"Final SOC:             {soc[-1]:.3f}")

    # -----------------------------
    # Plots (FULL YEAR) with month names on x-axis ✅
    # -----------------------------
    # 1) FULL YEAR: Load vs Served vs Grid Import
    plt.figure(figsize=(10, 4))
    plt.plot(df.index, df["P_load_MW"].values, label="Load (MW)")
    plt.plot(df.index, p_to_load, label="Served (MW)")
    plt.plot(df.index, p_grid_import, label="Grid Import (MW)")
    ax = plt.gca()
    format_month_axis(ax)
    plt.ylabel("Power (MW)")
    plt.title("2023: Load vs Served vs Grid Import")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hybrid_2023_load_served_import.png"), dpi=250)
    plt.close()

    # 2) FULL YEAR: Battery SOC
    plt.figure(figsize=(10, 4))
    plt.plot(df.index, soc)
    ax = plt.gca()
    format_month_axis(ax)
    plt.ylabel("SOC (0–1)")
    plt.title("2023: Battery SOC")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hybrid_2023_soc.png"), dpi=250)
    plt.close()

    # -----------------------------
    # Daily series + plots (month names) ✅
    # -----------------------------
    s_import = pd.Series(p_grid_import, index=df.index)
    s_curt = pd.Series(p_curt, index=df.index)

    daily_import = s_import.resample("D").sum() * dt_h
    daily_curt = s_curt.resample("D").sum() * dt_h

    # Daily grid import plot
    fig, ax = plt.subplots(figsize=(10, 4))
    daily_import.plot(ax=ax)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.set_xlabel("Month (2023)")
    ax.set_ylabel("Grid import (MWh/day)")
    ax.set_title("2023: Daily grid import")
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hybrid_2023_daily_grid_import.png"), dpi=250)
    plt.close()

    # Daily PV curtailment plot
    fig, ax = plt.subplots(figsize=(10, 4))
    daily_curt.plot(ax=ax)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.set_xlabel("Month (2023)")
    ax.set_ylabel("PV curtailment (MWh/day)")
    ax.set_title("2023: Daily PV curtailment")
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "hybrid_2023_daily_pv_curtailment.png"), dpi=250)
    plt.close()

    # -----------------------------
    # Daily averages split
    # -----------------------------
    daily_load = df["P_load_MW"].resample("D").sum() * dt_h
    daily_geo = pd.Series(p_geo_used, index=df.index).resample("D").sum() * dt_h
    daily_served = pd.Series(p_to_load, index=df.index).resample("D").sum() * dt_h
    daily_pv_batt = daily_served - daily_geo - daily_import

    print("\n=== Daily averages (FULL YEAR 2023) ===")
    print("Avg load (MWh/day):           ", daily_load.mean())
    print("Avg geo served (MWh/day):     ", daily_geo.mean())
    print("Avg PV+batt served (MWh/day): ", daily_pv_batt.mean())
    print("Avg grid import (MWh/day):    ", daily_import.mean())

    print("\nSaved plots in:", OUT_DIR)
    print("- hybrid_2023_load_served_import.png")
    print("- hybrid_2023_soc.png")
    print("- hybrid_2023_daily_grid_import.png")
    print("- hybrid_2023_daily_pv_curtailment.png")

if __name__ == "__main__":
    main()

