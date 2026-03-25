# Harrington Platform -- Operator Reference

Single source of truth for running all seven apps, ports, paths, code standards, and experimental parameters.

---

## Infrastructure

### IronMan (Dev Machine)

- OS: Ubuntu 24
- GPU: NVIDIA RTX 3080 (~10 GB VRAM)
- Compute stack: CuPy 14.0.1 (CUDA GPU), Numba 0.64.0 (12 CPU threads), NumPy 2.4.3
- Project root: `~/harrington/`
- Shared venv: `~/harrington/.venv` (sourced in .bashrc)
- Remote access: Tailscale at `ironman.tail4b9e00.ts.net` + VS Code Remote SSH
- ssh-agent configured for git

### Repo Map

| Repo | Port | Description |
|------|------|-------------|
| harrington-pax-americana | 8501 | Geopolitical predictions, intelligence council |
| harrington-wealth-management | 8502 | Retirement simulation (Rickman Sequence), budget suite |
| harrington-automation-station | 8503 | Lab hardware control, beam profiling, z-scan |
| harrington-labs | 8505 | Photonics lab simulators + LMI modeling (merged from harrington-lmi) |
| harrington-health | 8506 | Clinical dashboard, Quest lab parser, MELD/risk scores |
| harrington-common | -- | Shared theme, admin framework, compute (JIT), reporting (LaTeX/gnuplot/PDF) |
| harrington-infra | -- | Deployment, stress tests, cross-repo tooling |

### Launch

```bash
cd ~/harrington/<repo>
uv run streamlit run app/streamlit_app.py --server.port <port>
```

### Package Manager

All repos use uv. Shared workspace at `~/harrington/` with common `.venv`.

```bash
uv sync                    # install/update deps
uv add <package>           # add dependency
uv run <command>           # run in venv
```

Each repo has `harrington-common` as a workspace dep:
```toml
[tool.uv.sources]
harrington-common = { workspace = true }
```

### Git

```bash
git add -A && git commit -m "msg" && git push
```

GitHub: `jtharrington1997`. ssh-agent configured on IronMan.

### Syncthing

Data files synced via Syncthing to `data/` dirs. Each repo has `.stignore` for caches.

### Environment Variables

| Variable | Effect |
|----------|--------|
| `HARRINGTON_NO_JIT` | Force NumPy fallback (disable Numba) |
| `HARRINGTON_NO_CUDA` | Disable GPU (use Numba CPU) |
| `HARRINGTON_SERIAL` | Disable parallel_map |

---

## harrington-labs (port 8505)

### Pages

| # | Page | Description |
|---|------|-------------|
| 1 | Direct Diode Lab | L-I curves, thermal rollover, far-field, beam combining |
| 2 | Fiber Laser Lab | Gain modeling, nonlinear thresholds, thermal, beam combining |
| 3 | Pulsed Laser Lab | Ultrafast pulses, autocorrelation, GDD, z-scan, beam combining |
| 4 | Quantum Dots Lab | Brus bandgap, PL/absorption spectra, exciton dynamics |
| 5 | Beam Control Lab | Atmospheric propagation, Fried parameter, AO Strehl |
| 6 | Coatings Lab | Transfer matrix, spectral/angular reflectance, E-field, GDD |
| 7 | Advanced Spectroscopy Lab | Raman, Brillouin, DUVRR, LIBS, FTIR, hyperspectral |
| 10 | Demonstrator Builder | Resonator, QD fiber laser + beam combining, QD diode + beam combining, M&S |
| 11 | Modeling & Simulation | LMI workspace -- regime, beam propagation, nonlinear, thermal, z-scan, campaigns |
| 80 | Laser Library | 35 sources (lasers, lamps, LEDs, broadband) |
| 81 | Material Database | 27 materials with Sellmeier dispersion |
| 90 | Admin | API keys, data management, compute backend |

### Simulation Engines (all JIT-accelerated via harrington_common.compute)

11 engines in `src/harrington_labs/simulation/`: direct_diode, fiber_laser, beam_control, pulsed_laser, quantum_dots, coatings, beam_combining, spectroscopy, qd_fiber_laser, qd_diode_combiner. All have no Streamlit imports.

4 LMI engines in `src/harrington_labs/lmi/simulation/`: beam_propagation, nonlinear, thermal, custom_models.

### Cross-Lab Features

- Shared Beam State: configure source in one lab, share to others. All 7 labs receive; source labs (1-4) push.
- Source Database: 35 light sources with sidebar selector on every lab page.
- Material Database: 27 materials with sidebar selector on every lab page.
- Model Comparison: every lab has upload + compare panel (R2, RMSE, residuals).
- Reference Library: upload papers/datasheets on any lab page, persisted to `data/references/`.
- Beam Combining: all source labs include SBC and/or CBC. Shared `beam_combining.py` module.

### Dissertation Target

Sapphire 2100 nm / 5 mm open-aperture z-scan validation.

---

## harrington-wealth-management (port 8502)

Pages 1-5: Rickman Sequence retirement simulation (sequence-of-returns risk, FIA 0% floor).
Pages 6-11: Budget suite (Dashboard, Accounts/Transactions, Budget Planner, Bills/Subscriptions, Goals/Debt Payoff, Net Worth).
Page 12: Admin.

Data: `data/raw/Rickman_JTH_v2.xlsx`. Budget data persisted as JSON in `data/budget/`. Has `import_mint_csv()` for old Mint CSV format.

Built for Alliance Wealth Management.

---

## harrington-health (port 8506)

7 pages: Clinical Dashboard, Lab Trends, Record Explorer, MELD/Risk Scores, Report Generator, Data Upload, Admin.

Quest PDF parser + Quest CSV auto-detect (73 analyte aliases). Persistent data at `data/Quest_Simple_all.csv` (2221 records, 72 tests, 2021-2024).

Risk engines: MELD-Na, Child-Pugh, APRI, FIB-4. Clinical context: AIH, cirrhosis, portal HTN, splenomegaly, varices. Meds: azathioprine, naltrexone, prednisone.

---

## harrington-pax-americana (port 8501)

Pages: Overview, Video Library, Thesis Model, Predictions, Sector Monitor, News Cross-Ref, Intelligence Council, Market Research, Document Library, Settings, Admin, Trade Analyst.

Intelligence Council: Claude + ChatGPT independently assess predictions. Human-in-the-loop approval. Full audit trail.

Trade Analyst: Options recommendations, $2k budget model, position framework.

Admin password required for AI assessments, document approval, trade analysis.

---

## harrington-automation-station (port 8503)

Lab automation for laser characterization (z-scan, knife-edge).

Hardware: Newport SMC100/NSC100, Thorlabs KDC101, Ophir StarBright, BeamGage, DataRay, Galil, Lantronix.

Pending: admin API key management, auto port-scanning, supercluster expansion. Instrumentation roadmap: Pharos laser control, Andor spectrometer, NI DAQ, FPGA, ImageJ, COMSOL.

---

## Digital Twin: 8.5 um fs Laser on Si and Ge

### Experimental Setup

| Parameter | Value |
|-----------|-------|
| Wavelength | 8500 nm (8.5 um) |
| Photon energy | 0.146 eV |
| Pulse duration | 170 fs FWHM |
| Pulse energy | 20 uJ |
| Rep rate | 10 kHz |
| Average power | 200 mW |
| Peak power | ~118 MW |
| Focusing optic | 10 cm OAP |
| Input beam diameter | ~5 mm (1/e2) |
| Measured spot (1/e2) | 200 um diameter |
| Sample thickness | 0.1 mm |

### Silicon at 8.5 um

MPA order: 8-photon. n=3.42, n2=4.0e-14 cm2/W, alpha=0.001/cm.
P/Pcr ~ 8x -- self-focusing dominates. MPA negligible at this wavelength.

### Germanium at 8.5 um

MPA order: 5-photon. n=4.0, n2=2.0e-13 cm2/W, alpha=0.02/cm.
P/Pcr ~ 35x -- much stronger self-focusing. Lower melt threshold. More interesting sample.

### Measurement Priorities

1. Transmission (linear vs nonlinear deviation)
2. Beam profile after sample (self-focusing signatures)
3. Damage threshold (S-on-1 protocol)
4. Time-resolved pump-probe (two-temperature model validation)

---

## Code Standards (All Repos)

- `from __future__ import annotations` on every module
- Module-level docstrings
- No `sys.path` hacks -- all business logic in `src/`
- Admin gating via `require_admin()`
- `width="stretch"` on all `plotly_chart` calls (not deprecated `use_container_width`)
- No emojis -- use professional text markers [L], [W], [D], [B], [PENDING], etc.
- Plotly: `plotly_white` template with transparent background
- Streamlit: Americana theme (cream/navy/red)
- Physics engines: no Streamlit imports, JIT via `harrington_common.compute`
- `cupy-cuda12x` is always optional (`[cuda]` extra)
- Human-in-the-loop on all AI recommendations
- Full audit trails on AI-generated content
- Cost-conscious API usage (confirm before LLM calls)
- Individual patch files over full rezips when possible

---

## Key Formulas

Gaussian beam at focus:
- w0 = M2 * lambda * f / (pi * w_input)
- z_R = pi * w0^2 / (M2 * lambda)
- I_peak = P_peak / (pi * w0^2)
- F = E_pulse / (pi * w0^2)

Multiphoton absorption:
- N_photons = ceil(E_gap / E_photon)
- E_photon = 1240 / lambda_nm [eV]

Self-focusing:
- P_cr = 3.77 * lambda^2 / (8 * pi * n0 * n2)
- z_collapse ~ 0.367 * z_R / sqrt(sqrt(P/Pcr) - 0.852) [Marburger]

Thermal (fs pulse):
- dT_surface = F_absorbed / (rho * cp * l_heat)
- l_heat = max(sqrt(D * tau), 1/alpha)

Two-temperature model:
- Ce * dTe/dt = S(t) - G*(Te - Tl)
- Cl * dTl/dt = G*(Te - Tl)

B-integral:
- B = (2*pi/lambda) * n2 * I * L [radians]
