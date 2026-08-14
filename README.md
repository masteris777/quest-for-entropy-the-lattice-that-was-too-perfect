# Quest for Entropy #7 — The Lattice That Was Too Perfect

Companion code for the article *The Lattice That Was Too Perfect*.

A deterministic lattice of coupled pendulums (the sine-Gordon chain) builds a genuine
particle and genuine waves — and cannot jostle its own particle, because the hidden
order that builds the particle is the same order that stops the medium's waves from
ever getting a grip on it. This repo re-runs the experiments behind every number in
the article.

## Run it

```
pip install -r requirements.txt
python run_all.py
```

A few minutes. It runs the three kink experiments from scratch, checks every quoted
number against the fresh output, and re-derives the mass table from the frozen raw
evidence. Exits non-zero if anything drifted.

To regenerate the figures as well:

```
python kink_checks.py     # if not already run by run_all.py
python make_figures.py
python lattice_sheet.py   # the struck-sheet animation (2D sine-Gordon)
python kink_portrait.py   # the kink-with-weather animation (1D chain)
python ghost_shot_anim.py # the ghost-shot animation (1D chain)
python kink_vs_breather.py # the still kink vs the swinging breather (1D chain)
python ring_collapse.py   # the 2D ring of twist collapsing
```

## What is in here

| file | what it is |
|---|---|
| `kink_brownian.py` | the original bath integrator (2026-02), unmodified |
| `kink_checks.py` | the three bath/ghost-shot experiments; imports the integrator, never re-types it |
| `make_figures.py` | the article's figures |
| `lattice_sheet.py` | the 2D struck-sheet animation from the article |
| `kink_portrait.py`, `ghost_shot_anim.py` | the 1D chain animations from the article (the kink, the ghost shot) |
| `kink_vs_breather.py`, `ring_collapse.py` | the bestiary animations (kink stillness vs breather; the 2D ring collapse) |
| `ghost_shot_check.py` | measures the animation's own numbers: the ~2-pendulum nudge-and-park after the ghost shot |
| `run_all.py` | the reproduction gate |
| `kink_reference.json` | the numbers as published |
| `mass_comparison.json`, `lab18_summary.json` | frozen raw evidence for the mass table (see honesty notes) |
| `figures/`, `assets/` | the figures as published |

## Honesty notes

**What the bath numbers mean.** The integrator's diffusion-style fit returns a number at
every temperature, and those numbers reproduce here to five digits — but `kink_checks.py`
shows they are not diffusion: the damped bath gives one kick then the kink parks (MSD
exponent ~0.43 at every temperature, second-half position std exactly 0), the undamped bath
gives one kick then a ballistic cruise (exponent ~2), and a wave packet fired directly at
the kink passes through with ~99.9% of its energy (~0.02% reflected, kink displacement
+0.00). The medium cannot jostle its own particle; the fit was measuring a single kick.

**The mass table is frozen evidence, not a fresh run.** `mass_comparison.json` is the raw
output of the mass experiment (analytic vs inertially-measured kink mass across the
configurations). `run_all.py` re-derives the analytic column from the soliton formula
8*sqrt(alpha)/c and recomputes every relative error and the worst case (2.99%) from the raw
values — arithmetic on shipped evidence. The push-measurement itself was not re-executed for
this episode; that is the one number chain here that rests on a frozen file rather than a
fresh run.

**The bath is randomly seeded.** The phonon bath starts from a seeded RNG state. All the
randomness is in that initial state; the evolution afterwards is exact.

## Licence

Code MIT. Article text CC BY 4.0.
