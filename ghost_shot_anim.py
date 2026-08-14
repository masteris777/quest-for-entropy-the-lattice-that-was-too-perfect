"""The ghost shot: a wave packet fired straight at the kink passes through it.

    python ghost_shot_anim.py

1D sine-Gordon chain - the article's medium:

    u_tt = c^2 u_xx - alpha * sin(u)

Initial state: an exact kink standing mid-chain, and one deliberate wave packet
fired at it from the left. The packet goes through the particle; the twist stays.

WHAT THE ANIMATION MUST SHOW (visualization, no numbers quoted from it)
  V1  A wave packet travelling toward the standing twist.
  V2  The packet passing THROUGH the twist and coming out the other side.
  V3  The twist still standing at (essentially) the same place afterwards.
"""

import numpy as np

HERE = __import__("pathlib").Path(__file__).resolve().parent
ASSETS = HERE                      # the gif is written beside this script

N = 640                  # pendulums in the chain
C2 = 1.0                 # ripple speed squared (dx = 1)
ALPHA = 0.008            # gravity per pendulum -> kink width c/sqrt(alpha) ~ 11 sites
DT = 0.3
N_STEP = 1550
EVERY = 10
TWO_PI = 2.0 * np.pi


def simulate():
    x = np.arange(N, dtype=float)
    w = (C2 / ALPHA) ** 0.5
    u = 4.0 * np.arctan(np.exp((x - N / 2) / w))
    v = np.zeros(N)

    # the shot: one packet, fired from the left at the standing twist
    x0, k, amp = 110.0, 0.45, 0.85
    env = np.exp(-((x - x0) ** 2) / (2.0 * 12.0 ** 2))
    pkt = amp * env * np.cos(k * (x - x0))
    u += pkt
    vg = C2 * k / np.sqrt(C2 * k * k + ALPHA)
    v += -vg * np.gradient(pkt)

    frames = []
    for n in range(N_STEP):
        lap = np.zeros(N)
        lap[1:-1] = u[2:] - 2.0 * u[1:-1] + u[:-2]
        v += DT * (C2 * lap - ALPHA * np.sin(u))
        v[0] = v[-1] = 0.0
        u += DT * v
        u[0] = 0.0
        u[-1] = TWO_PI
        if n % EVERY == 0:
            frames.append(u.copy())
    return frames


def kink_center(u):
    i = int(np.argmin(np.abs(u - np.pi)))
    return float(i)


def render(frames):
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
        2, 1, figsize=(7.6, 3.2), facecolor="#0a1024",
        gridspec_kw={"height_ratios": [1.15, 1.0], "hspace": 0.08})
    for a in (top, bot):
        a.set_facecolor("#0a1024")
        a.set_xlim(0, N)
        for s in a.spines.values():
            s.set_color("#2a3a5f")
    top.set_ylim(-1.15, 1.15)
    top.set_xticks([]); top.set_yticks([])
    top.axhline(0.0, color="#2a3a5f", lw=1.0, zorder=1)

    u0 = frames[0][xs]
    q = top.quiver(xs, np.zeros_like(xs), np.sin(u0), -np.cos(u0),
                   angles="uv", scale_units="inches", scale=3.4,
                   pivot="middle", width=0.004, zorder=3)
    q.set_color(twistmap(np.clip(u0 / TWO_PI, 0, 1)))

    bot.set_ylim(-0.22, 1.3)
    bot.set_xticks([])
    bot.set_yticks([0, 1])
    bot.set_yticklabels(["flat", "one full\nturn"], fontsize=8.5, color="#9fb4d8")
    bot.tick_params(colors="#9fb4d8", length=0)
    bot.axhline(0.0, color="#2a3a5f", lw=0.8)
    bot.axhline(1.0, color="#2a3a5f", lw=0.8)
    (line,) = bot.plot(np.arange(N), frames[0] / TWO_PI, color="#7fc6cf", lw=2.0)
    mark = bot.axvline(kink_center(frames[0]), color="#ff9d5c", lw=1.0, ls="--",
                       alpha=0.85)
    bot.text(6, 1.16, "amount of twist along the chain", fontsize=8.5,
             color="#9fb4d8")
    fig.tight_layout()

    def draw(i):
        us = frames[i][xs]
        q.set_UVC(np.sin(us), -np.cos(us))
        q.set_color(twistmap(np.clip(us / TWO_PI, 0, 1)))
        line.set_ydata(frames[i] / TWO_PI)
        mark.set_xdata([kink_center(frames[i])])
        return [q, line, mark]

    anim = FuncAnimation(fig, draw, frames=len(frames), blit=True)
    out = ASSETS / "ghost_shot.gif"
    anim.save(out, writer=PillowWriter(fps=16))
    draw(len(frames) - 1)
    fig.savefig(HERE / "ghost_shot_preview.png", dpi=110, facecolor="#0a1024")
    print(f"wrote {out} and ghost_shot_preview.png")


if __name__ == "__main__":
    render(simulate())
