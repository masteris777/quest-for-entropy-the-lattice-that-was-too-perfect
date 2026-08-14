"""A sheet of pendulums, struck twice: real waves out of neighbours dragging neighbours.

    python lattice_sheet.py

2D sine-Gordon on a grid — the same medium as the article's chain, one dimension up:

    u_tt = c^2 (u_xx + u_yy) - alpha * sin(u)

Two simultaneous strikes. The rings spread, cross, interfere where they overlap, and
pass through each other. Nothing wave-like is assumed: each grid point only feels its
four neighbours and its own gravity.

WHAT THE ANIMATION MUST SHOW (visualization, no numbers quoted from it)
  V1  Circular ripples spreading from each strike at the medium's own speed.
  V2  The two ring systems crossing and passing through each other.
  V3  Interference where they overlap - bright and dark bands, two-source style.
"""

import numpy as np

HERE = __import__("pathlib").Path(__file__).resolve().parent
ASSETS = HERE                      # the gif is written beside this script

N = 420                  # grid points per side
C2 = 1.0                 # ripple speed squared (dx = 1)
ALPHA = 0.15             # gravity per pendulum
DT = 0.35
SEP = 55                 # half-distance between the two strikes
SIGMA = 3.0
AMP = 1.8                # strike strength (velocity impulse)
N_STEP = 440
EVERY = 5


def simulate():
    u = np.zeros((N, N))
    v = np.zeros((N, N))
    yy, xx = np.mgrid[0:N, 0:N]
    c = N // 2
    for sx in (c - SEP, c + SEP):
        r2 = (xx - sx) ** 2 + (yy - c) ** 2
        v += AMP * np.exp(-r2 / (2.0 * SIGMA ** 2))

    frames = []
    for n in range(N_STEP):
        lap = (np.roll(u, 1, 0) + np.roll(u, -1, 0)
               + np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4.0 * u)
        lap[0, :] = lap[-1, :] = lap[:, 0] = lap[:, -1] = 0.0
        v += DT * (C2 * lap - ALPHA * np.sin(u))
        u += DT * v
        u[0, :] = u[-1, :] = u[:, 0] = u[:, -1] = 0.0
        if n % EVERY == 0:
            frames.append(u.copy())
    return frames


def render(frames):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter
    from matplotlib.colors import LinearSegmentedColormap

    oil = LinearSegmentedColormap.from_list(
        "oil", ["#0a1a33", "#123055", "#2a6a8f", "#7fc6cf", "#eafcff"])

    fig, a = plt.subplots(figsize=(5.6, 5.6), facecolor="#0a1024")
    a.set_facecolor("#0a1024")
    a.set_xticks([]); a.set_yticks([])
    for s in a.spines.values():
        s.set_color("#2a3a5f")
    im = a.imshow(frames[0], origin="lower", cmap=oil, vmin=-0.28, vmax=0.38,
                  extent=(0, N, 0, N))
    fig.tight_layout()

    def draw(i):
        im.set_data(frames[i])
        return [im]

    anim = FuncAnimation(fig, draw, frames=len(frames), blit=True)
    out = ASSETS / "lattice_sheet.gif"
    anim.save(out, writer=PillowWriter(fps=16))
    draw(len(frames) - 1)
    fig.savefig(HERE / "lattice_sheet_preview.png", dpi=110, facecolor="#0a1024")
    print(f"wrote {out} and lattice_sheet_preview.png")


if __name__ == "__main__":
    render(simulate())
