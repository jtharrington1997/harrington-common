# Harrington Lab Platform — Operator Reference

Personal reference for running all five apps, building the digital twin,
and connecting experimental data. This is the single source of truth for
parameters, ports, paths, and procedures.

---

## Infrastructure

### IronMan (Dev Machine)

- **OS:** Ubuntu 24
- **GPU:** NVIDIA RTX 3080 (CUDA toolkit + numba + cupy)
- **Project root:** `~/Projects/`
- **Remote access:** Tailscale + VS Code Remote SSH
- **Hostname:** `ironman.tail4b9e00.ts.net`

### Repo Map

| Repo | Port (local) | Port (Tailscale HTTPS) | Domain |
|------|-------------|------------------------|--------|
| pax-americana | 8501 | 443 | Geopolitical predictions |
| rickman-sequence-demo | 8502 | 8443 | Retirement planning (Alliance Wealth) |
| automation-station | 8503 | 8444 | Lab hardware + beam profiling |
| harrington-lmi | 8504 | 8445 | Laser-material interaction modeling |
| harrington-common | — | — | Shared theme + admin framework |

### Launch / Stop All Apps

```bash
~/Projects/launch.sh           # start all four
~/Projects/launch.sh --serve   # start + Tailscale HTTPS exposure
~/Projects/launch.sh stop      # stop all
```

### Per-App Launch

```bash
cd ~/Projects/<repo>
uv run streamlit run app/streamlit_app.py
```

### Package Manager

All repos use **uv** (not pip, not poetry). Standard commands:

```bash
uv sync                    # install/update deps
uv add <package>           # add dependency
uv run <command>           # run in venv
```

Each repo has `harrington-common` as a local editable dep via:
```toml
[tool.uv.sources]
harrington-common = { path = "../harrington-common", editable = true }
```

### Git Workflow

```bash
git push --set-upstream origin main   # first push (autoSetupRemote=true globally)
git add -A && git commit -m "msg" && git push   # standard
```

GitHub: `jtharrington1997`

---

## Digital Twin: 8.5 um fs Laser on Si and Ge

### Your Experimental Setup

| Parameter | Value | Notes |
|-----------|-------|-------|
| Wavelength | 8500 nm (8.5 um) | Mid-IR |
| Photon energy | 0.146 eV | 1240 / 8500 |
| Pulse duration | 170 fs FWHM | |
| Pulse energy | 20 uJ | |
| Rep rate | 10 kHz | |
| Average power | 200 mW | E * f_rep |
| Peak power | ~118 MW | E / tau |
| Focusing optic | 10 cm OAP | Off-axis parabolic |
| Input beam diameter | ~5 mm (1/e2) | |
| Measured spot (1/e2) | 200 um diameter | Override in sidebar |
| f/# | ~10 | f / (2*w_in) |
| Sample thickness | 0.1 mm | Both Si and Ge |
| Ambient temp | 300 K | Room temp |

### Derived Quantities at Focus

| Quantity | Value | Formula |
|----------|-------|---------|
| Spot area | 3.14e-4 cm2 | pi * (100e-4)^2 |
| Fluence | ~63.7 mJ/cm2 | E / A |
| Peak irradiance | ~3.74e11 W/cm2 | P_peak / A |
| Rayleigh range | ~4.3 mm (in material) | pi * w0^2 * n / (M2 * lambda) |

### Silicon (Si) at 8.5 um

| Property | Value | Source / Notes |
|----------|-------|----------------|
| Bandgap | 1.12 eV (indirect) | Room temp |
| MPA order | 8-photon | ceil(1.12 / 0.146) |
| n at 8.5 um | 3.42 | Handbook value, transparent |
| n2 | 4.0e-14 cm2/W | Nonlinear refractive index |
| alpha (linear) | 0.001 /cm | Very low — transparent |
| Thermal conductivity | 148 W/mK | |
| Density | 2329 kg/m3 | |
| Specific heat | 710 J/kgK | |
| Thermal diffusivity | 8.8e-5 m2/s | k / (rho * cp) |
| Melting point | 1687 K | |
| Electron-phonon coupling | 1e17 W/m3K | For two-temp model |
| LIDT (ns pulses) | ~2 J/cm2 | Reference, scales with tau^0.5 |

**Key physics at your conditions:**
- 8-photon absorption is extremely weak (sigma ~ 1e-88). MPA is negligible for Si at this wavelength and irradiance.
- Linear absorption is also negligible (alpha = 0.001/cm, nearly transparent).
- Self-focusing: P_cr ~ 3.77 * lambda^2 / (8*pi*n*n2) ~ 15 MW. You're at ~118 MW, so P/Pcr ~ 8x. Self-focusing WILL occur. Collapse distance via Marburger formula is on the order of hundreds of um.
- Thermal: at 63.7 mJ/cm2, single-pulse dT is small because almost no energy is absorbed linearly. Multi-pulse accumulation at 10 kHz is also negligible.
- The dominant interaction is Kerr self-focusing leading to filamentation, not absorption.

### Germanium (Ge) at 8.5 um

| Property | Value | Source / Notes |
|----------|-------|----------------|
| Bandgap | 0.67 eV (indirect, L-point direct) | Room temp |
| MPA order | 5-photon | ceil(0.67 / 0.146) |
| n at 8.5 um | 4.0 | Handbook value |
| n2 | 2.0e-13 cm2/W | ~5x higher than Si |
| alpha (linear) | 0.02 /cm | Slightly absorbing |
| Thermal conductivity | 60 W/mK | |
| Density | 5323 kg/m3 | |
| Specific heat | 320 J/kgK | |
| Thermal diffusivity | 3.6e-5 m2/s | |
| Melting point | 1211 K | Lower than Si |
| Electron-phonon coupling | 1e16 W/m3K | |
| LIDT (ns pulses) | ~1 J/cm2 | Lower than Si |

**Key physics at your conditions:**
- 5-photon absorption is still very weak but orders of magnitude stronger than Si's 8-photon. May contribute at the highest irradiance near focus.
- Linear absorption (0.02/cm) gives penetration depth of 50 cm — essentially transparent, but 20x more absorbing than Si.
- Self-focusing: P_cr ~ 3.77 * lambda^2 / (8*pi*4.0*2e-13*1e-4) ~ 3.4 MW. P/Pcr ~ 35x. MUCH stronger self-focusing than Si. Collapse distance is shorter.
- Thermal: higher linear absorption + lower melting point + lower thermal conductivity = Ge is more vulnerable. Still unlikely to melt from single pulses at this fluence, but multi-pulse accumulation could matter.
- Ge is the more interesting sample: stronger nonlinear response, lower MPA order, lower melt threshold.

### What to Measure for Digital Twin Comparison

**Priority 1 — Transmission:**
- Measure transmitted power through each sample at 8.5 um
- Record incident power, transmitted power, spot size
- Compare against Beer-Lambert (linear) prediction
- Any deviation = nonlinear absorption signature

**Priority 2 — Beam profile after sample:**
- Image transmitted beam on a camera or knife-edge scan
- Look for self-focusing signatures: beam narrowing, hot spots, ring patterns
- Compare against input Gaussian profile

**Priority 3 — Damage threshold:**
- Ramp fluence until visible damage
- Record fluence at first damage for each material
- S-on-1 protocol: N pulses at each fluence level, vary N
- Compare against model melt threshold

**Priority 4 — Time-resolved (if available):**
- Pump-probe or transient reflectivity
- Maps to two-temperature model predictions
- Electron-lattice equilibration timescale (~1-10 ps)

### Feeding Data into Automation Station

The Digital Twin Compare page (automation-station port 8503, page 8) accepts:

**CSV upload format for beam profiles:**
```
x_um,intensity
-200,0.01
-180,0.03
...
```

**CSV for transmission:**
```
wavelength_nm,T
8500,0.45
```

**CSV for damage threshold:**
```
fluence_mj_cm2,damaged
10,0
20,0
40,0
60,1
80,1
```

Or use manual entry mode in the app.

### Material Properties You Should Verify/Update

The default values in `materials.py` are handbook estimates. For your specific samples, measure or look up:

- **Exact n at 8.5 um** — use FTIR or ellipsometry. Doping and crystal orientation matter.
- **Linear absorption at 8.5 um** — FTIR transmission on a thick sample. Free carrier absorption from doping can dominate.
- **Sample doping** — intrinsic? n-type? p-type? Resistivity? Free carrier absorption scales with doping.
- **Surface quality** — polished? AR coated? Roughness affects LIDT.
- **Crystal orientation** — (100), (111), (110)? Affects nonlinear coefficients.

To add custom values, use the Material Database page in LMI or edit `data/manual/materials.json` directly.

---

## App-Specific Reference

### Pax Americana (port 8501)

**Pages:** Overview, Video Library, Thesis Model, Predictions, Sector Monitor, News Cross-Ref, Intelligence Council, Market Research, Document Library, Settings, Admin, Trade Analyst

**Key data:** `data/manual/config.json` (API keys, watchlist), `data/cache/` (transcripts, summaries)

**Intelligence Council:** Claude + ChatGPT independently assess predictions. Human-in-the-loop approval. Full audit trail in `data/manual/council_assessments.json`.

**Trade Analyst:** Options recommendations, $2k budget model, position framework. Links to prediction IDs (E01-E14).

**Admin password required** for: generating AI assessments, approving documents, running trade analysis.

### Rickman Sequence Demo (port 8502)

**Pages:** Simulation, Market Monitor, News Feed, Methodology, Settings

**Data source:** `data/raw/Rickman_JTH_v2.xlsx`

**Key talking point:** Avg ROR vs Real ROR panel showing FIA 0% floor superiority under sequence-of-returns risk.

**Built for:** Alliance Wealth Management (allianceplanning.net)

### Automation Station (port 8503)

**Pages:** Full Auto, Semi Auto, Minimal, Results, Settings, Gnuplot, Admin, Digital Twin Compare

**Hardware:** Ophir StarBright (power meter), Newport SMC100 (Z stage), Thorlabs KDC101 (X knife-edge)

**Gnuplot:** Installed on IronMan. Scripts use Americana palette (cream bg, navy/red data).

**Results export:** CSV download from Results page. Gnuplot renders PNG from editable .gp scripts.

### Harrington LMI (port 8504)

**Pages:** Laser Library, Material Database, Interaction Analyzer, Source Builder, Simulation, Admin, Digital Twin

**Default lasers:** Nd:YAG CW/Q-switched, Ti:Sapph 800nm, CO2 10.6um, Er:Fiber 1550nm, Excimer KrF 248nm, HeNe 632.8nm, Yb:Fiber 1070nm

**Default materials:** Al, Cu, SS304, Si (with mid-IR), Ge (with mid-IR), GaAs, SiO2, BK7, LiNbO3, KTP, PMMA, Water

**Custom lasers/materials:** Saved to `data/manual/lasers.json` and `data/manual/materials.json`

**Digital Twin sidebar defaults:** Pre-loaded with your 8.5 um / 170 fs / 20 uJ / 10 kHz / 200 um spot parameters.

---

## Code Standards (All Repos)

- `from __future__ import annotations` on every module
- Module-level docstrings
- `io/store.py` for JSON I/O (pax, rickman)
- `io/config.py` for app config (automation-station, LMI)
- No `sys.path` hacks
- All business logic in `src/`
- Admin gating via `require_admin()`
- `use_container_width` replaced with `width="stretch"` on `plotly_chart` calls
- Individual patch files over full rezips when possible
- Human-in-the-loop control over all AI recommendations
- Full audit trails on AI-generated content
- Cost-conscious API usage (confirm before LLM calls)

---

## Quick Reference: Key Formulas

**Gaussian beam at focus:**
- w0 = M2 * lambda * f / (pi * w_input)
- z_R = pi * w0^2 / (M2 * lambda)
- I_peak = P_peak / (pi * w0^2)
- F = E_pulse / (pi * w0^2)

**Multiphoton absorption:**
- N_photons = ceil(E_gap / E_photon)
- E_photon = 1240 / lambda_nm  [eV]
- alpha_MPA = sigma_N * I^(N-1)

**Self-focusing:**
- P_cr = 3.77 * lambda^2 / (8 * pi * n0 * n2)
- z_collapse ~ 0.367 * z_R / sqrt(sqrt(P/Pcr) - 0.852)  [Marburger]

**Thermal (fs pulse, heat confined):**
- l_thermal = sqrt(D * tau)  [diffusion length during pulse]
- dT_surface = F_absorbed / (rho * cp * l_heat)
- l_heat = max(l_thermal, 1/alpha)

**Two-temperature model:**
- Ce * dTe/dt = S(t) - G*(Te - Tl)
- Cl * dTl/dt = G*(Te - Tl)
- Equilibration time ~ Ce / G  [typically 1-10 ps]

**B-integral:**
- B = (2*pi/lambda) * n2 * I * L  [radians]
- B > pi means significant self-phase modulation
