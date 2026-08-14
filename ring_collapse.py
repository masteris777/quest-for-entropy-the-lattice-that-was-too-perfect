"""The sheet cannot keep a lump: a ring of twist collapses, flashes, and dissolves.

    python ring_collapse.py

2D sine-Gordon on a grid - the same medium as the struck sheet:

    u_tt = c^2 (u_xx + u_yy) - alpha * sin(u)

Initial state: a disk of full twist (u = 2*pi inside radius R0, 0 outside), bounded
by a smooth ring wall. In the chain that wall would be a trapped kink; on the sheet
the wall has tension, so the ring is crushed by its own boundary: it shrinks,
flashes once at the centre, and dissolves into ordinary ripples.

WHAT THE ANIMATION MUST SHOW (visualization, no numbers quoted from it)
  V1  The ring of twist shrinking under its own wall tension.
  V2  The collapse flash at the centre.
  V3  Afterwards: no lump left - only ripples spreading outward.
"""

import numpy as np

HERE = __import__("pathlib").Path(__file__).resolve().parent
ASSETS = HERE                      # the gif is written beside this script

N = 300
C2 = 1.0
ALPHA = 0.05             # ring wall width ~ 4.5 sites
DT = 0.25
R0 = 45.0                # initial ring radius
N_STEP = 1400
EVERY = 8
TWO_PI = 2.0 * np.pi


def simulate():
    yy, xx = np.mgrid[0:N, 0:N]
    r = np.sqrt((xx - N / 2) ** 2 + (yy - N / 2) ** 2)
    w = (C2 / ALPHA) ** 0.5
    u = 4.0 * np.arctan(np.exp(-(r - R0) / w))
    v = np.zeros((N, N))

    # absorbing sponge at the borders, so outgoing debris leaves the scene
    # instead of reflecting back as a box pattern (display only - the physics
    # of the collapse happens long before anything reaches the edge)
    edge = np.minimum(np.minimum(xx, N - 1 - xx), np.minimum(yy, N - 1 - yy))
    sponge = np.where(edge < 50, 1.0 - 0.05 * ((50 - edge) / 50.0) ** 2, 1.0)

    frames = []
    for n in range(N_STEP):
        lap = (np.roll(u, 1, 0) + np.roll(u, -1, 0)
               + np.roll(u, 1, 1) + np.roll(u, -1, 1) - 4.0 * u)
        lap[0, :] = lap[-1, :] = lap[:, 0] = lap[:, -1] = 0.0
        v += DT * (C2 * lap - ALPHA * np.sin(u))
        v *= sponge
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

    cmap = LinearSegmentedColormap.from_list(
        "twistfield", ["#7fd4ff", "#123055", "#0a1024", "#3a2a4f", "#ff9d5c"])

    def squash(u):
        # sqrt-compressed display so the 2*pi lump and the ~0.3 rad ripple
        # debris are both visible in one colour scale
        return np.sign(u) * np.sqrt(np.abs(u))

    fig, a = plt.subplots(figsize=(5.6, 5.6), facecolor="#0a1024")
    a.set_facecolor("#0a1024")
    a.set_xticks([]); a.set_yticks([])
    for s in a.spines.values():
        s.set_color("#2a3a5f")
    im = a.imshow(squash(frames[0]), origin="lower", cmap=cmap,
                  vmin=-2.6, vmax=2.6, extent=(0, N, 0, N))
    fig.tight_layout()

    def draw(i):
        im.set_data(squash(frames[i]))
        return [im]

    anim = FuncAnimation(fig, draw, frames=len(frames), blit=True)
    out = ASSETS / "ring_collapse.gif"
    anim.save(out, writer=PillowWriter(fps=16))
    for tag, idx in (("start", 0), ("flash", 40), ("end", len(frames) - 1)):
        draw(idx)
        fig.savefig(HERE / f"ring_collapse_preview_{tag}.png", dpi=110,
                    facecolor="#0a1024")
    print(f"wrote {out} and 3 previews")


if __name__ == "__main__":
    render(simulate())
