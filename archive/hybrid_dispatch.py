import pandas as pd
import numpy as np

def simulate_hybrid(
    df,
    P_geo_MW=0.25,          # geothermal net power (MW) baseline
    E_batt_MWh=2.0,         # battery energy capacity
    P_batt_max_MW=0.5,      # battery max charge/discharge power
    eta_c=0.95,             # charge efficiency
    eta_d=0.95,             # discharge efficiency
    soc0=0.50,              # initial SOC fraction
    dt_h=1.0
):
    """
    Dispatch rule (simple):
    - Geothermal is constant baseload P_geo_MW.
    - PV adds on top.
    - If PV surplus -> charge battery (limited by P_batt_max, remaining capacity)
    - If PV deficit (optional) -> you may discharge to support a target. For now we export all geo+pv and only charge from surplus PV.
    """

    n = len(df)
    soc = np.zeros(n)
    P_charge = np.zeros(n)      # MW (positive means charging)
    P_discharge = np.zeros(n)   # MW (positive means discharging)
    P_to_grid = np.zeros(n)     # MW exported
    P_curt = np.zeros(n)        # MW curtailed PV

    E = soc0 * E_batt_MWh
    soc[0] = soc0

    for i in range(n):
        P_pv = float(df["P_pv_MW"].iloc[i])
        P_in = P_geo_MW + P_pv

        # For now: Always export geothermal, and export PV unless battery can store surplus above some export limit.
        # Simple version: charge battery with PV (no export limit), so only curtail when battery is full and PV still exists.
        surplus_pv = P_pv  # treat PV as storable if battery has space

        # Max charging possible due to power limit and available PV
        Pch = min(P_batt_max_MW, surplus_pv)

        # Max charging due to remaining capacity
        cap_left = E_batt_MWh - E
        Pch_cap = cap_left / dt_h  # MW
        Pch = min(Pch, Pch_cap)

        # Update battery energy (charge)
        E += (Pch * eta_c) * dt_h
        E = max(0.0, min(E, E_batt_MWh))

        P_charge[i] = Pch
        P_curt[i] = max(0.0, P_pv - Pch)

        # Export = geothermal + (PV used directly not stored) = geo + (PV - charged - curtailed)
        P_to_grid[i] = P_geo_MW + max(0.0, P_pv - Pch - P_curt[i])

        soc[i] = E / E_batt_MWh if E_batt_MWh > 0 else 0.0

    out = df.copy()
    out["P_geo_MW"] = P_geo_MW
    out["P_charge_MW"] = P_charge
    out["P_discharge_MW"] = P_discharge
    out["P_curt_MW"] = P_curt
    out["P_grid_MW"] = P_to_grid
    out["SOC"] = soc
    return out
