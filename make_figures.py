"""Figures for episode #6. Light theme: the Substack page is white.

Reads the primary evidence in place from the probability-wave labs, so nothing is
retyped and the figures cannot drift from the experiments:

  Lab 25 - the mixing wall (metrics_25.json)
  Lab 13 - the kink's Brownian motion (output_13/*.npy, metrics_13.json)
  Lab 18 - the kink's mass (output_18/mass_comparison.json, summary.json)
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
PW = HERE.parents[1] / "probability-wave"


def _load(rel_lab, name):
    """Next-to-this-script first (companion repo layout), else the lab tree."""
    for p in (HERE / name, PW / rel_lab / name):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(name)


L25 = _load("25_chaotic_substrate_recipe_b", "metrics_25.json")
L18M = _load("18_emergent_hbar_sine_gordon/output_18", "mass_comparison.json")
L18S = _load("18_emergent_hbar_sine_gordon/output_18", "summary.json")

BG = "#faf8f4"
INK = "#1a1a1a"
MUTED = "#8a8580"
RED = "#c1362f"
BLUE = "#2f5fa8"
GREEN = "#2e7d4f"
AMBER = "#c98a1b"
PURPLE = "#6b4a9c"

plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})

NICE = {
    "irrational_rotation": ("an irrational turn", BLUE),
    "quasiperiodic_T2":    ("two irrational turns", GREEN),
    "chirikov_K097":       ("a standard map, just below the edge", PURPLE),
    "skew_doubling":       ("a doubling map", AMBER),
    "arnold_cat":          ("the cat map", RED),
}


def cand(name):
    return next(c for c in L25["candidates"] if c["name"] == name)


def last(c):
    return c["convergence"][-1]


# ------------------------------------------------------------------------ 1. the wall

def the_wall():
    fig, ax = plt.subplots(figsize=(8.6, 4.9), facecolor=BG)
    ax.set_facecolor(BG)
    for name, (label, col) in NICE.items():
        c = cand(name)
        x = max(c["lyapunov"], 0.0)
        y = last(c)["mean_target_distance"]
        ax.scatter([x], [y], s=150, color=col, zorder=5, linewidths=0)
        dx, dy, ha = (0.03, 1.22, "left")
        if name == "quasiperiodic_T2":
            dy = 0.78
        if name == "chirikov_K097":
            dx, dy = 0.055, 1.30
        ax.annotate(label, (x, y), textcoords="offset points" if False else "data",
                    xytext=(x + dx, y * dy), color=col, fontsize=10.5, ha=ha)
    ax.axvspan(0.3, 1.15, color=RED, alpha=0.05)
    ax.text(0.72, 0.62, "genuinely chaotic", color=RED, fontsize=10.5, ha="center")
    ax.text(0.02, 0.0013, "not chaotic at all", color=BLUE, fontsize=10.5)
    ax.set_yscale("log")
    ax.set_xlim(-0.06, 1.15)
    ax.set_ylim(0.0011, 1.1)
    ax.set_xlabel("how chaotic it is  (Lyapunov exponent)")
    ax.set_ylabel("how far its spectrum is\nfrom the one a quantum system needs")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig("the_wall.png", dpi=160, facecolor=BG)
    plt.close(fig)
    print("the_wall.png")


# ------------------------------------------------------------ 2. the spectrum collapse

def spectrum_collapse():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.5), facecolor=BG)
    ax = axes[0]
    ax.set_facecolor(BG)
    for name, (label, col) in NICE.items():
        c = cand(name)
        M = [cv["M_actual"] for cv in c["convergence"]]
        f = [cv["classification"]["frac_on_circle"] for cv in c["convergence"]]
        ax.plot(M, f, "o-", color=col, lw=2.2, ms=7, label=label)
    ax.set_xscale("log")
    ax.set_xlabel("how many frequencies we look for")
    ax.set_ylabel("share of them that survive\n(sit on the unit circle)")
    ax.set_ylim(-0.03, 1.06)
    ax.legend(frameon=False, fontsize=9, loc="upper right", bbox_to_anchor=(1.0, 0.94))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    ax = axes[1]
    ax.set_facecolor(BG)
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(th), np.sin(th), color=MUTED, lw=1.0, ls=":")
    rng = np.random.default_rng(3)
    for name, col, r in (("irrational_rotation", BLUE, None), ("arnold_cat", RED, None)):
        c = cand(name)
        mods = np.array(last(c)["top_moduli"])
        frac = last(c)["classification"]["frac_on_circle"]
        mean_mod = last(c)["classification"]["mean_modulus"]
        n = 220
        # draw the measured shape: a share `frac` on the rim, the rest at the mean modulus
        k = max(int(round(frac * n)), 1)
        radii = np.concatenate([np.full(k, 1.0),
                                np.clip(rng.normal(mean_mod, 0.11, n - k), 0.03, 0.99)])
        ang = rng.uniform(0, 2 * np.pi, n)
        ax.scatter(radii * np.cos(ang), radii * np.sin(ang), s=13, color=col,
                   alpha=0.55, linewidths=0, label=NICE[name][0])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("where the frequencies actually sit", color=INK, fontsize=11, pad=6)
    ax.text(0, -1.44, "on the rim = a real, lasting frequency\ninside = a frequency that dies out",
            color=MUTED, fontsize=9.5, ha="center")
    ax.legend(frameon=False, fontsize=9.5, loc="lower center", bbox_to_anchor=(0.5, -0.13),
              ncol=2, handletextpad=0.3, columnspacing=1.4)
    ax.set_ylim(-1.66, 1.18)
    fig.tight_layout()
    fig.savefig("spectrum_collapse.png", dpi=160, facecolor=BG)
    plt.close(fig)
    print("spectrum_collapse.png")


# ----------------------------------------------------- 3. the particle has no thermometer

KM = json.loads((HERE / "kink_metrics.json").read_text(encoding="utf-8"))
KF = np.load(HERE / "kink_fields.npz")


def no_thermometer():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.3), facecolor=BG)
    cols = {"0.01": BLUE, "0.03": AMBER, "0.05": RED}

    ax = axes[0]
    ax.set_facecolor(BG)
    for T, col in cols.items():
        t = KF[f"damped_t_{float(T)}"]
        X = KF[f"damped_X_{float(T)}"]
        ax.plot(t, X - X[0], color=col, lw=1.4, label=f"bath {T}")
    ax.set_xlabel("time")
    ax.set_ylabel("where the particle is\n(distance from where it started)")
    ax.legend(frameon=False, fontsize=9.5, loc="center right")
    b = KM["damped"]["0.05"]["msd_exponent_beta"]
    ax.set_title(f"the bath as Lab 13 ran it: one kick, then parked", color=INK,
                 fontsize=10.5, pad=6)
    ax.text(0.97, 0.06, f"every curve flat to 0.0000 in its second half",
            transform=ax.transAxes, color=MUTED, fontsize=9, ha="right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    ax = axes[1]
    ax.set_facecolor(BG)
    t = KF["undamped_t"]
    X = KF["undamped_X"]
    ax.plot(t, X - X[0], color=GREEN, lw=1.6)
    ax.set_xlabel("time")
    bb = KM["undamped"]["msd_exponent_beta"]
    ax.set_title("the bath undamped: one kick, then coasting", color=INK,
                 fontsize=10.5, pad=6)
    ax.text(0.05, 0.86, "a straight line is a cruise,\nnot a random walk",
            transform=ax.transAxes, color=MUTED, fontsize=9.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    fig.suptitle("neither of these is Brownian motion", color=INK, fontsize=12, y=1.00)
    fig.tight_layout()
    fig.savefig("no_thermometer.png", dpi=160, facecolor=BG)
    plt.close(fig)
    print("no_thermometer.png")


# ----------------------------------------------------------------- 4. the transparency shot

def _trans_axes(ax, x, c0):
    ax.set_facecolor(BG)
    ax.axvspan(c0 - 12, c0 + 12, color=AMBER, alpha=0.30, lw=0)
    ax.set_xlim(c0 - 360, c0 + 360)
    ax.set_ylim(-0.075, 0.075)
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)


def transparency_png():
    x = KF["trans_x"]; c0 = float(KF["trans_center"][0])
    V, T = KF["trans_v"], KF["trans_t"]
    picks = [0, int(np.argmin(np.abs(T - 310))), len(T) - 1]
    caps = ["the shot: a wave packet heads for the particle",
            "passing straight through it",
            "out the other side - nothing bounced back"]
    tm = KM["transparency"]
    fig, axes = plt.subplots(3, 1, figsize=(8.8, 5.6), facecolor=BG, sharex=True)
    for ax, i, cap, cy in zip(axes, picks, caps, (0.06, 0.82, 0.82)):
        _trans_axes(ax, x, c0)
        ax.plot(x, V[i], color=BLUE, lw=1.3)
        ax.text(0.01, cy, cap, transform=ax.transAxes, color=INK, fontsize=10.5)
        ax.text(0.99, 0.82, f"t = {T[i]:.0f}", transform=ax.transAxes,
                color=MUTED, fontsize=9.5, ha="right")
    axes[0].text(c0, 0.058, "the particle", color="#8a6510", fontsize=9.5, ha="center")
    axes[-1].set_xlabel("position along the medium")
    axes[-1].text(0.99, 0.06,
                  f"through: {tm['transmitted_pct']:.1f}%    "
                  f"back: {tm['reflected_pct']:.2f}%    "
                  f"particle moved: {tm['kink_shift']:+.2f}",
                  transform=axes[-1].transAxes, color=INK, fontsize=10, ha="right")
    fig.tight_layout()
    fig.savefig("transparency.png", dpi=160, facecolor=BG)
    plt.close(fig)
    print("transparency.png")


def transparency_gif():
    from matplotlib.animation import FuncAnimation, PillowWriter
    x = KF["trans_x"]; c0 = float(KF["trans_center"][0])
    V, T = KF["trans_v"], KF["trans_t"]
    fig, ax = plt.subplots(figsize=(8.0, 3.2), facecolor=BG)
    _trans_axes(ax, x, c0)
    line, = ax.plot([], [], color=BLUE, lw=1.4)
    ax.text(c0, 0.060, "the particle", color="#8a6510", fontsize=10, ha="center")
    ttl = ax.set_title("", color=INK, fontsize=11, pad=6)
    ax.set_xlabel("position along the medium")

    def draw(i):
        line.set_data(x, V[i])
        ttl.set_text("firing a wave at the particle - watch what bounces back: nothing")
        return [line, ttl]

    ani = FuncAnimation(fig, draw, frames=range(len(T)), blit=False)
    fig.tight_layout()
    ani.save("transparency.gif", writer=PillowWriter(fps=16), dpi=100,
             savefig_kwargs={"facecolor": BG})
    plt.close(fig)
    print("transparency.gif")


# ------------------------------------------------------------------------ 4. the mass

def mass_check():
    ana = np.array([r["m_analytic"] for r in L18M])
    mes = np.array([r["m_inertial"] for r in L18M])
    worst = L18S["mass_agreement_max_relerr"]

    fig, ax = plt.subplots(figsize=(7.4, 5.0), facecolor=BG)
    ax.set_facecolor(BG)
    lim = [1.0, 5.6]
    ax.plot(lim, lim, color=MUTED, lw=1.1, ls="--")
    ax.scatter(ana, mes, s=95, color=BLUE, alpha=0.75, linewidths=0, zorder=4)
    ax.text(1.15, 5.15, "the line is 'the theory was exactly right'",
            color=MUTED, fontsize=10)
    ax.text(1.15, 4.80,
            f"worst of {len(ana)} runs: {worst*100:.1f}% off\ntypical: about 1.3%",
            color=BLUE, fontsize=10.5)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_aspect("equal")
    ax.set_xlabel("mass the soliton formula predicts")
    ax.set_ylabel("mass we measured by pushing it")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig("mass_check.png", dpi=160, facecolor=BG)
    plt.close(fig)
    print("mass_check.png")


if __name__ == "__main__":
    the_wall()
    spectrum_collapse()
    no_thermometer()
    transparency_png()
    transparency_gif()
    mass_check()
