import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def simulate_hybrid(
    df,
    p_geo_mw=0.24,
    p_load_mw=0.30,
    e_batt_mwh=8.0,
    p_batt_max_mw=0.20,
    eta_charge=0.95,
    eta_discharge=0.95,
    soc0=0.50,
):
    dt_h = df.index.to_series().diff().median().total_seconds() / 3600.0
    n = len(df)

    energy = soc0 * e_batt_mwh
    soc = np.zeros(n)
    grid_import = np.zeros(n)
    pv_curt = np.zeros(n)
    batt_charge = np.zeros(n)
    batt_discharge = np.zeros(n)
    renewable_to_load = np.zeros(n)

    for i, p_pv in enumerate(df["P_pv_MW"].astype(float).values):
        remaining = p_load_mw

        geo_to_load = min(p_geo_mw, remaining)
        remaining -= geo_to_load

        pv_to_load = min(p_pv, remaining)
        remaining -= pv_to_load
        pv_left = p_pv - pv_to_load

        charge = min(pv_left, p_batt_max_mw)
        max_charge_by_energy = max(0.0, (e_batt_mwh - energy) / (dt_h * eta_charge))
        charge = min(charge, max_charge_by_energy)
        energy += charge * dt_h * eta_charge
        pv_left -= charge

        discharge = min(remaining, p_batt_max_mw)
        max_discharge_by_energy = max(0.0, energy * eta_discharge / dt_h)
        discharge = min(discharge, max_discharge_by_energy)
        energy -= discharge * dt_h / eta_discharge
        remaining -= discharge

        grid_import[i] = max(0.0, remaining)
        pv_curt[i] = max(0.0, pv_left)
        batt_charge[i] = charge
        batt_discharge[i] = discharge
        renewable_to_load[i] = geo_to_load + pv_to_load + discharge
        soc[i] = energy / e_batt_mwh

    out = df.copy()
    out["SOC"] = soc
    out["P_grid_import_MW"] = grid_import
    out["P_pv_curt_MW"] = pv_curt
    out["P_batt_charge_MW"] = batt_charge
    out["P_batt_discharge_MW"] = batt_discharge
    out["P_renewable_to_load_MW"] = renewable_to_load
    return out, dt_h

if __name__ == "__main__":
    df = pd.read_csv("data/nuernberg_pv_2023_hourly.csv", index_col=0, parse_dates=True)
    out, dt_h = simulate_hybrid(df)
    out.to_csv("data/hybrid_dispatch_2023.csv")

    e_load = 0.30 * len(out) * dt_h
    e_grid = out["P_grid_import_MW"].sum() * dt_h
    e_curt = out["P_pv_curt_MW"].sum() * dt_h
    renewable_fraction = 1.0 - e_grid / e_load

    print("Grid import, MWh:", e_grid)
    print("PV curtailment, MWh:", e_curt)
    print("Renewable fraction:", renewable_fraction)
