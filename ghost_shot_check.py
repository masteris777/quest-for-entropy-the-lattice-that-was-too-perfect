"""Check: after the ghost-shot ripple passes, do the kink's arrows return to the
exact same angles, or did the kink pick up a small position shift?

    python ghost_shot_check.py
"""

import numpy as np
from ghost_shot_anim import simulate, N, TWO_PI


def center_subgrid(u):
    i = int(np.argmax(u > np.pi))
    # linear interpolation of the pi-crossing between sites i-1 and i
    u0, u1 = u[i - 1], u[i]
    return (i - 1) + (np.pi - u0) / (u1 - u0)


frames = simulate()
first, last = frames[0], frames[-1]

c0, c1 = center_subgrid(first), center_subgrid(last)
print(f"kink centre at start : {c0:.3f} sites")
print(f"kink centre at end   : {c1:.3f} sites")
print(f"net shift            : {c1 - c0:+.3f} sites")

core = slice(int(c0) - 30, int(c0) + 30)
diff = np.abs(last - first)[core]
print(f"max angle change in the kink core, first vs last frame: "
      f"{diff.max():.4f} rad ({np.degrees(diff.max()):.2f} deg)")

# and the late-time motion: is anything still swinging at the end?
tail = np.abs(frames[-1] - frames[-5])
print(f"max change over the last ~120 steps, whole chain: {tail.max():.5f} rad")
