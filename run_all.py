"""Reproduce every claim episode #7 makes, from scratch.

    python run_all.py

Runs the three kink experiments (which import the original bath integrator,
unmodified), then checks every number the article quotes against the fresh
output, and re-derives the mass table from the frozen raw evidence. Exits
non-zero if anything has drifted.

Needs numpy and scipy. Regenerating the figures additionally needs matplotlib and
pillow; run_all.py does not require them. A few minutes.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
fails = []


def check(name, got, want, tol=0.0):
    ok = (got == want) if tol == 0 else (got is not None and abs(got - want) <= tol)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}\n         got {got!r}, expected {want!r}")
    if not ok:
        fails.append(name)


def flag(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{'  (' + detail + ')' if detail else ''}")
    if not ok:
        fails.append(name)


print("1. the kink experiments (importing the original bath integrator) ...\n")
subprocess.run([sys.executable, "kink_checks.py"], cwd=HERE, check=True)
K = json.loads((HERE / "kink_metrics.json").read_text(encoding="utf-8"))
RK = json.loads((HERE / "kink_reference.json").read_text(encoding="utf-8"))

print("\n   the bath experiments:\n")
for T in ("0.01", "0.03", "0.05"):
    check(f"bath {T}: the diffusion-style fit reproduces",
          K["damped"][T]["D_lab13_estimator"], RK["damped"][T]["D_lab13_estimator"],
          0.02 * RK["damped"][T]["D_lab13_estimator"])
    flag(f"bath {T}: but it is one kick, then parked",
         K["damped"][T]["std_second_half"] < 1e-3
         and abs(K["damped"][T]["msd_exponent_beta"] - 1.0) > 0.3,
         f"beta={K['damped'][T]['msd_exponent_beta']:.3f}, "
         f"second-half std={K['damped'][T]['std_second_half']:.4f}")
flag("undamped bath: one kick, then coasting (ballistic, not Brownian)",
     abs(K["undamped"]["msd_exponent_beta"] - 2.0) < 0.15,
     f"beta={K['undamped']['msd_exponent_beta']:.3f}")

print("\n   the ghost shot:\n")
tp = K["transparency"]
flag("the wave passes through the particle", tp["transmitted_pct"] > 99.0,
     f"{tp['transmitted_pct']:.1f}% through")
flag("almost nothing reflects", tp["reflected_pct"] < 0.5,
     f"{tp['reflected_pct']:.2f}% back")
flag("the particle does not move", abs(tp["kink_shift"]) < 0.5,
     f"moved {tp['kink_shift']:+.2f}")

print("\n2. the mass table, re-derived from the frozen raw evidence ...\n")
MC = json.loads((HERE / "mass_comparison.json").read_text(encoding="utf-8"))
S18 = json.loads((HERE / "lab18_summary.json").read_text(encoding="utf-8"))
worst = 0.0
ok_all = True
for row in MC:
    m_formula = 8.0 * math.sqrt(row["alpha"]) / row["c"]
    ok_all &= abs(m_formula - row["m_analytic"]) < 1e-9
    rel = abs(row["m_inertial"] - row["m_analytic"]) / row["m_analytic"]
    worst = max(worst, rel)
flag("the stored analytic masses ARE the soliton formula 8*sqrt(alpha)/c", ok_all,
     f"{len(MC)} configurations")
check("worst measured-vs-formula disagreement (the 2.99%)",
      round(worst, 4), round(S18["mass_agreement_max_relerr"], 4), 1e-4)
flag("worst case is under 3 percent", worst < 0.03, f"{100*worst:.2f}%")

print("\n" + ("-" * 62))
if fails:
    print(f"{len(fails)} CHECK(S) FAILED: {', '.join(fails)}")
    sys.exit(1)
print("all checks reproduced")
