# pv_download_nuernberg_2023.py
# Download PVGIS hourly data for Nürnberg for the FULL YEAR 2023
# and compute PV power for a 1.0 MWp PV system. Saves a CSV you can use in your hybrid model.

import os
import pandas as pd
import pvlib

# -----------------------------
# SETTINGS
# -----------------------------
LAT, LON = 49.4521, 11.0767   # Nürnberg (approx)
YEAR = 2023

PV_MW = 1.0       # PV system size in MWp
PR = 0.85         # Performance ratio (losses). 0.80–0.90 typical

OUT_DIR = "data"
OUT_CSV = os.path.join(OUT_DIR, f"nuernberg_pv_{YEAR}_hourly.csv")
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    # PVGIS hourly (full year). This requests ONLY 2024.
    # Note: PVGIS returns irradiance in W/m^2 typically.
    data, meta = pvlib.iotools.get_pvgis_hourly(
        LAT,
        LON,
        start=YEAR,
        end=YEAR,
        components=True,   # get direct + diffuse components
        surface_tilt=30,   # you can change (e.g., 25–35 for Germany)
        surface_azimuth=180,  # south-facing
        usehorizon=True,
        pvcalculation=False  # we will compute PV ourselves
    )

    df = data.copy()

    # Ensure DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"])
            df = df.set_index("time")
        else:
            raise ValueError("Could not find a datetime index or a 'time' column.")

    # Keep ONLY 2023 (safety)
    df = df[(df.index.year == YEAR)]

    # PVGIS “plane of array” components (typical column names)
    needed = ["poa_direct", "poa_sky_diffuse", "poa_ground_diffuse"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Missing PVGIS columns: {missing}. Found columns: {list(df.columns)}")

    # POA global irradiance (W/m^2)
    df["poa_global_Wm2"] = df["poa_direct"] + df["poa_sky_diffuse"] + df["poa_ground_diffuse"]

    # Simple PV power model:
    # P(MW) = PV_MW * PR * (G_poa / 1000)
    # clip at PV_MW (cannot exceed nameplate)
    df["P_pv_MW"] = PV_MW * PR * (df["poa_global_Wm2"] / 1000.0)
    df["P_pv_MW"] = df["P_pv_MW"].clip(lower=0.0, upper=PV_MW)

    # Save CSV
    df.to_csv(OUT_CSV)

    # Quick summary (hourly timestep assumed)
    dt_h = df.index.to_series().diff().median().total_seconds() / 3600.0
    pv_energy_mwh = df["P_pv_MW"].sum() * dt_h
    pv_max_mw = df["P_pv_MW"].max()

    print("Saved:", OUT_CSV)
    print("Year:", YEAR)
    print("Rows:", len(df))
    print("Detected dt_h (hours):", dt_h)
    print(f"Total PV Energy in {YEAR} for {PV_MW} MWp (PR={PR}): {pv_energy_mwh:.2f} MWh")
    print(f"Max PV Power in {YEAR}: {pv_max_mw:.3f} MW")
    print("Columns:", list(df.columns))

if __name__ == "__main__":
    main()
