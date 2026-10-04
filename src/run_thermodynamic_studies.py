import subprocess
import sys

scripts = [
    "src/pressure_sweep.py",
    "src/pressure_map.py",
    "src/off_design_and_startup.py",
]

for script in scripts:
    print(f"Running {script}...")
    result = subprocess.run([sys.executable, script], check=False)
    if result.returncode != 0:
        raise SystemExit(f"{script} failed with exit code {result.returncode}")

print("Thermodynamic studies completed.")
