import os
import pandas as pd
import pvlib

LAT = 49.4521
LON = 11.0767
YEAR = 2023
PV_MW = 1.0
PR = 0.85

OUT_DIR = "data"
OUT_CSV = os.path.join(OUT_DIR, f"nuernberg_pv_{YEAR}_hourly.csv")
os.makedirs(OUT_DIR, exist_ok=True)

data, meta = pvlib.iotools.get_pvgis_hourly(
    LAT,
    LON,
    start=YEAR,
    end=YEAR,
    components=True,
    surface_tilt=30,
    surface_azimuth=180,
    usehorizon=True,
    pvcalculation=False,
)

df = data.copy()
df = df[df.index.year == YEAR]

components = ["poa_direct", "poa_sky_diffuse", "poa_ground_diffuse"]
df["poa_global_Wm2"] = df[components].sum(axis=1)
df["P_pv_MW"] = PV_MW * PR * (df["poa_global_Wm2"] / 1000.0)
df["P_pv_MW"] = df["P_pv_MW"].clip(lower=0.0, upper=PV_MW)
df.to_csv(OUT_CSV)

dt_h = df.index.to_series().diff().median().total_seconds() / 3600.0
print("Annual PV energy, MWh:", df["P_pv_MW"].sum() * dt_h)
