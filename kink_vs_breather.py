"""Two ways to be stationary: the kink (truly still) vs the breather (swings in place).

    python kink_vs_breather.py

1D sine-Gordon chain - the article's medium:

    u_tt = c^2 u_xx - alpha * sin(u)

Top: the kink - a static balance of forces. Every pendulum sits where its neighbours'
spring twist exactly cancels gravity. Integrated numerically: nothing moves.
Bottom: the breather - sine-Gordon's other localized object. Started from the exact
breather initial data; the pendulums swing forever while the lump goes nowhere.

WHAT THE ANIMATION MUST SHOW (visualization, no numbers quoted from it)
  V1  The kink's arrows perfectly frozen for the whole run (a static solution).
  V2  The breather's arrows swinging periodically while the lump stays in place.
  V3  Neither object drifts or spreads.
"""

import numpy as np

HERE = __import__("pathlib").Path(__file__).resolve().parent
ASSETS = HERE                      # the gif is written beside this script

N = 600                  # pendulums per chain
C2 = 1.0                 # ripple speed squared (dx = 1)
ALPHA = 0.008            # gravity per pendulum -> kink width ~ 11 sites
DT = 0.3
N_STEP = 1600
EVERY = 10
OMEGA = 0.6              # breather internal frequency (rescaled units), amplitude ~ 3.7 rad
TWO_PI = 2.0 * np.pi


def evolve(u, v, top_bc):
    frames = []
    for n in range(N_STEP):
        lap = np.zeros(N)
        lap[1:-1] = u[2:] - 2.0 * u[1:-1] + u[:-2]
        v += DT * (C2 * lap - ALPHA * np.sin(u))
        v[0] = v[-1] = 0.0
        u += DT * v
        u[0] = 0.0
        u[-1] = top_bc
        if n % EVERY == 0:
            frames.append(u.copy())
    return frames


def simulate():
    x = np.arange(N, dtype=float)

    # the kink: exact static solution, integrated anyway - it must not move
    w = (C2 / ALPHA) ** 0.5
    uk = 4.0 * np.arctan(np.exp((x - N / 2) / w))
    kink = evolve(uk, np.zeros(N), TWO_PI)

    # the breather: exact initial data at its zero-crossing (u=0, v=breather velocity)
    eta = np.sqrt(1.0 - OMEGA ** 2) / OMEGA
    k = np.sqrt(ALPHA * (1.0 - OMEGA ** 2))
    v0 = 4.0 * np.sqrt(ALPHA) * eta * OMEGA / np.cosh(k * (x - N / 2))
    breather = evolve(np.zeros(N), v0, 0.0)

    return kink, breather


def render(kink, breather):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    from matplotlib.colors import LinearSegmentedColormap

    twistmap = LinearSegmentedColormap.from_list(
        "twist", ["#7fc6cf", "#b9d98a", "#ffd166", "#ff9d5c"])

    step = 10
    xs = np.arange(0, N, step)

    fig, (top, bot) = plt.subplots(
        2, 1, figsize=(7.6, 2.9), facecolor="#0a1024",
        gridspec_kw={"hspace": 0.15})
    for a in (top, bot):
        a.set_facecolor("#0a1024")
        a.set_xlim(0, N)
        a.set_ylim(-1.25, 1.25)
        a.set_xticks([]); a.set_yticks([])
        for s in a.spines.values():
            s.set_color("#2a3a5f")
        a.axhline(0.0, color="#2a3a5f", lw=1.0, zorder=1)

    quivers = []
    for a, frames, wrap in ((top, kink, TWO_PI), (bot, breather, 0.0)):
        u0 = frames[0][xs]
        q = a.quiver(xs, np.zeros_like(xs), np.sin(u0), -np.cos(u0),
                     angles="uv", scale_units="inches", scale=3.6,
                     pivot="middle", width=0.004, zorder=3)
        quivers.append(q)
    fig.tight_layout()

    def paint(q, us, span):
        q.set_UVC(np.sin(us), -np.cos(us))
        q.set_color(twistmap(np.clip(np.abs(us) / span, 0, 1)))

    def draw(i):
        paint(quivers[0], kink[i][xs], TWO_PI)
        paint(quivers[1], breather[i][xs], TWO_PI)
        return quivers

    draw(0)
    anim = FuncAnimation(fig, draw, frames=len(kink), blit=True)
    out = ASSETS / "kink_vs_breather.gif"
    anim.save(out, writer=PillowWriter(fps=16))
    draw(len(kink) - 1)
    fig.savefig(HERE / "kink_vs_breather_preview.png", dpi=110, facecolor="#0a1024")
    print(f"wrote {out} and kink_vs_breather_preview.png")


if __name__ == "__main__":
    kink, breather = simulate()
    drift = float(np.abs(kink[-1] - kink[0]).max())
    print(f"kink max change over the whole run: {drift:.2e} rad (a static solution)")
    render(kink, breather)
