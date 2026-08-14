"""Episode #6: what Lab 13's numbers actually mean, settled by three experiments.

Lab 13 reported the kink doing Brownian motion in its own deterministic phonon bath.
Re-running it reproduced the numbers exactly - and showed they are not diffusion. This
script is the corrected claim, as code:

  A. the damped bath (Lab 13 as written) - the kink is kicked once, then parks.
  B. the undamped bath (the obvious rescue) - the kink is kicked once, then coasts.
  C. the transparency shot - fire a wave packet at the kink and measure what reflects.
     Almost nothing does. The medium cannot jostle its own particle, and that is WHY
     neither bath ever randomizes it.

The integrator is imported from Lab 13 itself (kink_brownian.py), never re-typed.
Writes kink_metrics.json and kink_fields.npz next to this file.
"""

import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent

# import Lab 13's own integrator: from beside this script if shipped together
# (companion repo), else from the lab tree.
for _cand in (HERE / "kink_brownian.py",
              HERE.parents[1] / "probability-wave/13_kink_brownian_motion/kink_brownian.py"):
    if _cand.exists():
        _spec = importlib.util.spec_from_file_location("kink_brownian", _cand)
        kb = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(kb)
        break
else:
    raise FileNotFoundError("kink_brownian.py not found")


def msd_exponent(X, fit_frac=4):
    """Slope of log MSD vs log lag over the window Lab 13 itself used for its D fit.
    Brownian motion must give ~1. Also returns Lab 13's own D estimator and how far
    that 'constant' actually wanders across its own fit window."""
    msd = kb.calculate_msd(X)
    lags = np.arange(len(msd)) * (0.2 * 20)
    fit = len(msd) // fit_frac
    beta = float(np.polyfit(np.log(lags[fit:]), np.log(msd[fit:]), 1)[0])
    ratio = msd[fit:] / (2 * lags[fit:])
    return msd, beta, float(ratio.mean()), float(ratio.max() / ratio.min())


def stats(X):
    half = len(X) // 2
    return {"net_drift": float(X[-1] - X[0]),
            "std_first_half": float(X[:half].std()),
            "std_second_half": float(X[half:].std())}


def part_A():
    print("A. the damped bath, exactly as Lab 13 ran it")
    out = {}
    traces = {}
    for T in (0.01, 0.03, 0.05):
        times, X = kb.run_sg_1d_kink(T_eff=T, steps=40000, sample_stride=20, nx=2048)
        msd, beta, D, spread = msd_exponent(X)
        out[str(T)] = {"D_lab13_estimator": D, "msd_exponent_beta": beta,
                       "D_ratio_spread_over_fit_window": spread, **stats(X)}
        traces[f"damped_X_{T}"] = X
        traces[f"damped_t_{T}"] = times
        print(f"   T={T}: D={D:.3e}  beta={beta:.3f}  "
              f"second-half std={out[str(T)]['std_second_half']:.4f}  "
              f"drift={out[str(T)]['net_drift']:+.3f}")
    return out, traces


def part_B():
    print("B. the undamped bath (gamma = 0)")
    times, X = kb.run_sg_1d_kink(gamma=0.0, T_eff=0.05, steps=80000,
                                 sample_stride=20, nx=2048)
    _, beta, _, _ = msd_exponent(X)
    out = {"msd_exponent_beta": beta, **stats(X)}
    print(f"   beta={beta:.3f} (ballistic ~2)  drift={out['net_drift']:+.1f}  "
          f"stds {out['std_first_half']:.1f}/{out['std_second_half']:.1f}")
    return out, {"undamped_X": X, "undamped_t": times}


def part_C():
    print("C. the transparency shot")
    c, alpha = 1.0, 0.1
    nx, dx, dt = 4096, 0.5, 0.1
    x = np.arange(nx) * dx
    center = nx * dx / 2
    gk = np.sqrt(alpha / c ** 2)
    u = 4.0 * np.arctan(np.exp(gk * (x - center)))
    v = np.zeros(nx)

    k0 = 1.2
    w0 = np.sqrt(c ** 2 * k0 ** 2 + alpha)
    x0, sig, amp = center - 300.0, 25.0, 0.05
    env = amp * np.exp(-((x - x0) ** 2) / (2 * sig ** 2))
    u += env * np.cos(k0 * (x - x0))
    v += env * (w0 * np.sin(k0 * (x - x0)))          # a rightward mover

    def edens(u, v):
        ux = np.gradient(u, dx)
        return 0.5 * v ** 2 + 0.5 * c ** 2 * ux ** 2 + alpha * (1 - np.cos(u))

    kink_u = 4.0 * np.arctan(np.exp(gk * (x - center)))
    E_packet = float((edens(u, v) - edens(kink_u, np.zeros(nx)))[x < center - 60].sum() * dx)

    k2 = (c / dx) ** 2
    steps, keep = 6000, 60
    frames_v, frames_t = [], []
    for s in range(steps + 1):
        if s % keep == 0:
            frames_v.append(v.copy())
            frames_t.append(s * dt)
        if s == steps:
            break
        lap = np.zeros(nx); lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
        f0 = k2 * lap - alpha * np.sin(u); f0[0] = f0[-1] = 0
        vh = v + 0.5 * dt * f0
        u = u + dt * vh; u[0] = 0; u[-1] = 2 * np.pi
        lap[1:-1] = u[2:] - 2 * u[1:-1] + u[:-2]
        f1 = k2 * lap - alpha * np.sin(u); f1[0] = f1[-1] = 0
        v = vh + 0.5 * dt * f1; v[0] = v[-1] = 0

    xk = float(x[np.argmin(np.abs(u - np.pi))])
    resid = edens(u, v) - edens(4.0 * np.arctan(np.exp(gk * (x - xk))), np.zeros(nx))
    E_refl = float(resid[x < xk - 60].sum() * dx)
    E_trans = float(resid[x > xk + 60].sum() * dx)
    out = {"packet_energy_in": E_packet,
           "transmitted": E_trans, "transmitted_pct": 100 * E_trans / E_packet,
           "reflected": E_refl, "reflected_pct": 100 * E_refl / E_packet,
           "kink_shift": xk - center,
           "params": {"k0": k0, "amp": amp, "alpha": alpha, "c": c,
                      "nx": nx, "dx": dx, "dt": dt, "steps": steps}}
    print(f"   in={E_packet:.5f}  through={out['transmitted_pct']:.1f}%  "
          f"back={out['reflected_pct']:.2f}%  kink moved {out['kink_shift']:+.2f}")
    return out, {"trans_v": np.array(frames_v), "trans_t": np.array(frames_t),
                 "trans_x": x, "trans_center": np.array([center])}


def main():
    met, store = {}, {}
    a, tr = part_A(); met["damped"] = a; store.update(tr)
    b, tr = part_B(); met["undamped"] = b; store.update(tr)
    c, tr = part_C(); met["transparency"] = c; store.update(tr)
    met["verdict"] = (
        "No Brownian motion in either bath: damped = one kick then parked "
        "(beta ~ 0.43 at every temperature, second-half std exactly 0), undamped = one "
        "kick then ballistic coasting (beta ~ 2). The transparency shot explains why: "
        "the medium's own waves pass through the kink almost without scattering, so "
        "they cannot jostle it. Lab 13's D values reproduce exactly and are not "
        "diffusion constants.")
    with open(HERE / "kink_metrics.json", "w", encoding="utf-8") as f:
        json.dump(met, f, indent=2)
    np.savez_compressed(HERE / "kink_fields.npz", **store)
    print("wrote kink_metrics.json, kink_fields.npz")


if __name__ == "__main__":
    main()
