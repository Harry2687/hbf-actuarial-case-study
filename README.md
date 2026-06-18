# HBF Actuarial Case Study: Financial & Portfolio Analysis (CY 2025 – 2026)

This repository contains an end-to-end actuarial analysis and interactive presentation evaluating the financial performance, product movements, Risk Equalisation dynamics, and clinical drivers of HBF’s Private Health Insurance (PHI) portfolio (covering Hospital and Extras products) across CY 2025 and 2026.

---

## Repository Structure

The project is split into a Python data pipeline and a web-based Reveal.js presentation:

```
├── 202503 HBF Case Study VALUES 1.xlsx  # Raw actuarial case study data
├── DATA_INFO.md                         # Descriptions of data fields & actuarial rules
├── BRAND_GUIDELINES.md                  # HBF color palettes and style rules
├── actuarial_analysis_report.md         # Comprehensive text report of the findings
├── analysis_output/                     # Generated summary CSVs and analytical datasets
├── src/                                 # Python pipeline source code
│   ├── loader.py                        # Excel data ingestion and type normalization
│   ├── financials.py                    # Calculations for margins, loss ratios, and frequencies
│   ├── movements.py                     # Policy roll-forward checks and migration pivots
│   ├── clinical.py                      # Clinical category ranking, psychiatric analysis, seasonality
│   ├── visuals.py                       # Altair visualization generator (exports interactive charts)
│   └── main.py                          # Pipeline runner coordinating all stages
└── presentation/                        # Reveal.js interactive slideshow (Vite + JavaScript)
    ├── index.html                       # Slide deck layout & copy
    ├── main.js                          # Reveal.js initialization
    ├── style.css                        # Slide custom typography & HBF theme styles
    └── public/                          # Directory for served interactive Altair chart embeds
```

---

## Getting Started

### 1. Run the Actuarial Pipeline (Python)

Ensure you have [uv](https://github.com/astral-sh/uv) installed.

Run the pipeline to clean the data, calculate actuarial metrics, output summaries to `analysis_output/`, and generate charts for the presentation:

```bash
uv run python -m src.main
```

### 2. Launch the Presentation (Vite + Reveal.js)

The presentation features interactive data visualizations generated directly from the analysis. To run the slideshow locally:

```bash
cd presentation
npm install
npm run dev
```

Open `http://localhost:5173` (or the URL shown in your terminal) to view the slides.
