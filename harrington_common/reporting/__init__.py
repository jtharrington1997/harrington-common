"""Shared reporting infrastructure for the Harrington ecosystem.

Provides LaTeX document generation, gnuplot figure export,
and PDF compilation utilities consumable by all apps.
Designed for the Linux/nvim/uv toolchain.

No Streamlit imports.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Report data structures ───────────────────────────────────────


@dataclass
class ReportSection:
    """A section in a generated report."""
    title: str
    content: str = ""
    level: int = 1  # 1=section, 2=subsection, 3=subsubsection
    figures: list[str] = field(default_factory=list)  # paths to figure files
    tables: list[str] = field(default_factory=list)  # LaTeX table strings


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    title: str = "Harrington Report"
    author: str = "Joey Harrington"
    date: str = ""
    document_class: str = "article"
    font_size: str = "11pt"
    geometry: str = "margin=1in"
    packages: list[str] = field(default_factory=lambda: [
        "longtable", "booktabs", "graphicx", "hyperref",
        "xcolor", "fancyhdr", "titlesec",
    ])
    header_left: str = ""
    header_right: str = ""
    logo_path: str = ""
    custom_preamble: str = ""


# ── LaTeX generation ─────────────────────────────────────────────

def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    replacements = {
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def _section_cmd(level: int) -> str:
    return {1: "section", 2: "subsection", 3: "subsubsection"}.get(level, "section")


def build_latex(
    sections: list[ReportSection],
    config: ReportConfig | None = None,
) -> str:
    """Build a complete LaTeX document from sections."""
    if config is None:
        config = ReportConfig()

    date_str = config.date or datetime.now().strftime("%B %d, %Y")
    packages = "\n".join(f"\\usepackage{{{p}}}" for p in config.packages)

    preamble = f"""\\documentclass[{config.font_size}]{{{config.document_class}}}
\\usepackage[{config.geometry}]{{geometry}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{lmodern}}
{packages}

% Harrington branding colors
\\definecolor{{hwnavy}}{{HTML}}{{1A3A5C}}
\\definecolor{{hwred}}{{HTML}}{{8B2332}}
\\definecolor{{hwgold}}{{HTML}}{{B8860B}}

% Section formatting
\\titleformat{{\\section}}{{\\Large\\bfseries\\color{{hwnavy}}}}{{\\thesection}}{{1em}}{{}}
\\titleformat{{\\subsection}}{{\\large\\bfseries\\color{{hwnavy}}}}{{\\thesubsection}}{{1em}}{{}}

% Header/footer
\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyhead[L]{{\\small\\color{{hwnavy}}{config.header_left or config.title}}}
\\fancyhead[R]{{\\small\\color{{gray}}{config.header_right or date_str}}}
\\fancyfoot[C]{{\\thepage}}
\\renewcommand{{\\headrulewidth}}{{0.5pt}}

% Hyperlinks
\\hypersetup{{colorlinks=true,linkcolor=hwnavy,urlcolor=hwnavy}}

{config.custom_preamble}

\\title{{\\color{{hwnavy}}{_escape_latex(config.title)}}}
\\author{{{_escape_latex(config.author)}}}
\\date{{{date_str}}}
"""

    body_lines = ["\\begin{document}", "\\maketitle", ""]

    for section in sections:
        cmd = _section_cmd(section.level)
        body_lines.append(f"\\{cmd}{{{_escape_latex(section.title)}}}")

        if section.content:
            body_lines.append(section.content)
            body_lines.append("")

        for table in section.tables:
            body_lines.append(table)
            body_lines.append("")

        for fig_path in section.figures:
            body_lines.append(f"""\\begin{{figure}}[htbp]
\\centering
\\includegraphics[width=0.9\\textwidth]{{{fig_path}}}
\\end{{figure}}""")
            body_lines.append("")

    body_lines.append("\\end{document}")

    return preamble + "\n" + "\n".join(body_lines)


def latex_table(
    headers: list[str],
    rows: list[list[str]],
    caption: str = "",
    alignment: str = "",
) -> str:
    """Build a LaTeX booktabs table."""
    n_cols = len(headers)
    if not alignment:
        alignment = "l" * n_cols

    lines = []
    if caption:
        lines.append(f"\\begin{{table}}[htbp]")
        lines.append(f"\\caption{{{_escape_latex(caption)}}}")
        lines.append(f"\\centering")

    lines.append(f"\\begin{{tabular}}{{{alignment}}}")
    lines.append("\\toprule")
    lines.append(" & ".join(f"\\textbf{{{_escape_latex(h)}}}" for h in headers) + " \\\\")
    lines.append("\\midrule")

    for row in rows:
        cells = [_escape_latex(str(c)) for c in row]
        lines.append(" & ".join(cells) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")

    if caption:
        lines.append("\\end{table}")

    return "\n".join(lines)


# ── Gnuplot generation ───────────────────────────────────────────

@dataclass
class GnuplotSeries:
    """A data series for gnuplot."""
    name: str
    x: list[float]
    y: list[float]
    style: str = "linespoints"
    linewidth: int = 2
    color: str = ""


@dataclass
class GnuplotSpec:
    """Specification for a gnuplot figure."""
    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    series: list[GnuplotSeries] = field(default_factory=list)
    x_log: bool = False
    y_log: bool = False
    terminal: str = "svg"
    width: int = 1200
    height: int = 800
    grid: bool = True


# Harrington brand colors for gnuplot
GP_COLORS = ["#1a3a5c", "#8b2332", "#b8860b", "#2d6a4f", "#7b4f8a", "#c96e12"]


def write_gnuplot_bundle(
    spec: GnuplotSpec,
    outdir: str | Path,
    stem: str = "plot",
) -> dict[str, Path]:
    """Write gnuplot data file and script. Returns paths dict."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    dat_path = outdir / f"{stem}.dat"
    gp_path = outdir / f"{stem}.gp"

    # Write data file
    with dat_path.open("w", encoding="utf-8") as f:
        for idx, s in enumerate(spec.series):
            f.write(f"# series {idx}: {s.name}\n")
            for x, y in zip(s.x, s.y):
                f.write(f"{x}\t{y}\n")
            if idx < len(spec.series) - 1:
                f.write("\n\n")

    # Determine output extension
    ext = {"svg": "svg", "pngcairo": "png", "pdfcairo": "pdf",
           "epslatex": "tex"}.get(spec.terminal, "svg")

    # Build plot commands
    plot_cmds = []
    for idx, s in enumerate(spec.series):
        color = s.color or GP_COLORS[idx % len(GP_COLORS)]
        plot_cmds.append(
            f"'{dat_path.name}' index {idx} using 1:2 "
            f"with {s.style} linewidth {s.linewidth} "
            f"linecolor rgb '{color}' title '{s.name}'"
        )

    gp_script = f"""# Harrington gnuplot — {spec.title}
set terminal {spec.terminal} size {spec.width},{spec.height} enhanced font 'Source Sans 3,14'
set output '{stem}.{ext}'
set title '{spec.title}' font ',16'
set xlabel '{spec.xlabel}'
set ylabel '{spec.ylabel}'
{"set grid" if spec.grid else "unset grid"}
{"set logscale x" if spec.x_log else ""}
{"set logscale y" if spec.y_log else ""}
set key outside right top
set style line 1 linewidth 2

plot {", ".join(plot_cmds)}
"""
    gp_path.write_text(gp_script, encoding="utf-8")

    return {"data": dat_path, "script": gp_path, "output": outdir / f"{stem}.{ext}"}


def run_gnuplot(script_path: str | Path) -> subprocess.CompletedProcess:
    """Execute a gnuplot script."""
    return subprocess.run(
        ["gnuplot", str(script_path)],
        cwd=str(Path(script_path).parent),
        capture_output=True, text=True,
    )


# ── PDF compilation ──────────────────────────────────────────────

def compile_latex_to_pdf(
    tex_content: str,
    output_path: str | Path,
    engine: str = "pdflatex",
    runs: int = 2,
) -> Path:
    """Compile LaTeX string to PDF.

    Args:
        tex_content: Complete LaTeX document string.
        output_path: Desired output PDF path.
        engine: LaTeX engine (pdflatex, xelatex, lualatex).
        runs: Number of compilation passes (2 for TOC/refs).

    Returns:
        Path to the generated PDF.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "report.tex"
        tex_path.write_text(tex_content, encoding="utf-8")

        for i in range(runs):
            result = subprocess.run(
                [engine, "-interaction=nonstopmode", "-output-directory", tmpdir, str(tex_path)],
                capture_output=True, text=True, cwd=tmpdir,
            )
            if result.returncode != 0 and i == runs - 1:
                raise RuntimeError(
                    f"LaTeX compilation failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
                )

        pdf_src = Path(tmpdir) / "report.pdf"
        if pdf_src.exists():
            shutil.copy2(pdf_src, output_path)
        else:
            raise FileNotFoundError(f"PDF not produced by {engine}")

    return output_path


def compile_tex_file(
    tex_path: str | Path,
    engine: str = "pdflatex",
    runs: int = 2,
) -> Path:
    """Compile an existing .tex file to PDF in the same directory."""
    tex_path = Path(tex_path)
    outdir = tex_path.parent

    for i in range(runs):
        result = subprocess.run(
            [engine, "-interaction=nonstopmode", "-output-directory", str(outdir), str(tex_path)],
            capture_output=True, text=True, cwd=str(outdir),
        )
        if result.returncode != 0 and i == runs - 1:
            raise RuntimeError(f"LaTeX compilation failed:\n{result.stdout[-2000:]}")

    pdf_path = outdir / tex_path.with_suffix(".pdf").name
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not produced: {pdf_path}")
    return pdf_path


# ── Report builder (high-level) ──────────────────────────────────

def build_report_pdf(
    sections: list[ReportSection],
    output_path: str | Path,
    config: ReportConfig | None = None,
    gnuplot_specs: list[tuple[str, GnuplotSpec]] | None = None,
) -> Path:
    """Build a complete PDF report with optional gnuplot figures.

    Args:
        sections: Report sections with content and tables.
        output_path: Final PDF location.
        config: Report configuration.
        gnuplot_specs: List of (stem, spec) pairs for gnuplot figures.
            Generated figures are automatically included in the report.

    Returns:
        Path to the generated PDF.
    """
    output_path = Path(output_path)

    # Generate gnuplot figures if requested
    if gnuplot_specs:
        fig_dir = output_path.parent / "figures"
        fig_dir.mkdir(parents=True, exist_ok=True)

        for stem, spec in gnuplot_specs:
            # Use pdfcairo for LaTeX inclusion
            spec.terminal = "pdfcairo"
            bundle = write_gnuplot_bundle(spec, fig_dir, stem)
            result = run_gnuplot(bundle["script"])

            if result.returncode == 0 and bundle["output"].exists():
                # Find or create a section to attach this figure
                for section in sections:
                    if stem.lower() in section.title.lower():
                        section.figures.append(str(bundle["output"].relative_to(output_path.parent)))
                        break
                else:
                    # Attach to last section if no title match
                    if sections:
                        sections[-1].figures.append(
                            str(bundle["output"].relative_to(output_path.parent))
                        )

    tex = build_latex(sections, config)
    return compile_latex_to_pdf(tex, output_path)
