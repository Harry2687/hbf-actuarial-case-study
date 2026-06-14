# %% [markdown]
# # HBF Actuarial Case Study: Interactive Walkthrough
# Walkthrough of the case study analysis step-by-step in VS Code's interactive Jupyter window.

# %% [markdown]
# ## 1. Setup & Data Ingestion
# Loads and cleans all sheets from the Excel file.

# %%
import polars as pl
from src.loader import get_cleaned_data

data = get_cleaned_data("202503 HBF Case Study VALUES 1.xlsx")
for name, df in data.items():
    print(f" - {name:15} | Shape: {df.shape}")

# %% [markdown]
# ## 2. Hospital Financial Analysis & Risk Equalisation
# Computes the hospital actuarial summary and margins.

# %%
from src.financials import calculate_hospital_financials

calculate_hospital_financials(data).select(
    [
        "Hosp",
        "Hosp Excess",
        "policies_start",
        "policies_end",
        "policy_growth_pct",
        "qtr_premium_per_policy",
        "qtr_freq_per_policy",
        "severity_per_episode",
        "qtr_re_per_policy",
        "gross_loss_ratio",
        "net_loss_ratio",
        "margin_pct",
        "qtr_margin_per_policy",
    ]
)

# %% [markdown]
# ## 3. Extras Financial Analysis
# Computes the extras actuarial summary and margins.

# %%
from src.financials import calculate_extras_financials

calculate_extras_financials(data).select(
    [
        "Extras",
        "policies_start",
        "policies_end",
        "policy_growth_pct",
        "qtr_premium_per_policy",
        "qtr_services_per_policy",
        "severity_per_service",
        "loss_ratio",
        "margin_pct",
        "qtr_margin_per_policy",
    ]
)

# %% [markdown]
# ## 4. Policy Movements & Attrition Profiling
# Reconciles policy changes with movements and prints the movement pivots.

# %%
from src.movements import (
    check_policy_movements_reconciliation,
    get_hosp_movements_pivot,
    get_ext_movements_pivot,
)

recon = check_policy_movements_reconciliation(data)
print(
    f"Reconciled | Hospital: {recon['hosp_reconciles']} | Extras: {recon['ext_reconciles']}"
)

print("\n--- HOSPITAL MOVEMENTS ---")
print(get_hosp_movements_pivot(data))

print("\n--- EXTRAS MOVEMENTS ---")
print(get_ext_movements_pivot(data))

# %% [markdown]
# ## 5. Clinical Claim Categories & Silver 0 Psychiatry Deep-Dive
# Summarizes hospital and extras claims, highlighting Silver 0's psychiatry waiver anomaly.

# %%
from src.clinical import (
    get_top_hospital_categories,
    get_extras_categories,
    get_silver_vs_gold_psychiatry,
)

print("--- TOP 5 HOSPITAL CLINICAL CATEGORIES ---")
print(get_top_hospital_categories(data).head(5))

print("\n--- TOP 5 EXTRAS CLAIM CATEGORIES ---")
print(get_extras_categories(data).head(5))

psych_data = get_silver_vs_gold_psychiatry(data)
print("\n--- SILVER 0 CLAIM MIX (Psychiatry Waiver) ---")
print(psych_data["silver_0"].head(3))

print("\n--- GOLD 0 CLAIM MIX (General) ---")
print(psych_data["gold_0"].head(3))

# %% [markdown]
# ## 6. Claims Seasonality
# Extracts quarterly claims seasonality for Hospital and Extras (limit resets).

# %%
from src.clinical import get_claims_seasonality

print("--- CLAIMS SEASONALITY BY QUARTER ---")
print(get_claims_seasonality(data))

# %% [markdown]
# ## 7. HBF Portfolio Quarterly Margin Trend
# Computes the overall quarterly HBF portfolio margins.

# %%
hosp_qtr = (
    data["policies"]
    .filter(pl.col("Hosp") != "No Hospital Prod")
    .group_by("Qtr")
    .agg(pl.col("hospital_income").sum().alias("hosp_prem"))
    .join(
        data["hosp_claims"]
        .group_by("Qtr")
        .agg(pl.col("TOTAL_BENEFIT").sum().alias("hosp_claims")),
        on="Qtr",
    )
    .join(
        data["re_data"]
        .group_by("Qtr")
        .agg(pl.col("RE Received").sum().alias("hosp_re")),
        on="Qtr",
    )
    .with_columns(
        (pl.col("hosp_prem") - pl.col("hosp_claims") + pl.col("hosp_re")).alias(
            "hosp_margin"
        )
    )
)
ext_qtr = (
    data["policies"]
    .filter(pl.col("Extras") != "No Extras Product")
    .group_by("Qtr")
    .agg(pl.col("extras_income").sum().alias("ext_prem"))
    .join(
        data["ext_claims"]
        .group_by("Qtr")
        .agg(pl.col("TOTAL_BENEFIT").sum().alias("ext_claims")),
        on="Qtr",
    )
    .with_columns((pl.col("ext_prem") - pl.col("ext_claims")).alias("ext_margin"))
)
hbf_total = (
    hosp_qtr.join(ext_qtr, on="Qtr")
    .with_columns(
        [
            (pl.col("hosp_prem") + pl.col("ext_prem")).alias("total_prem"),
            (pl.col("hosp_claims") + pl.col("ext_claims")).alias("total_claims"),
            (pl.col("hosp_margin") + pl.col("ext_margin")).alias("total_margin"),
            (
                (pl.col("hosp_margin") + pl.col("ext_margin"))
                / (pl.col("hosp_prem") + pl.col("ext_prem"))
            ).alias("total_margin_pct"),
        ]
    )
    .sort("Qtr")
)
print("--- HBF TOTAL PORTFOLIO QUARTERLY MARGINS ---")
print(
    hbf_total.select(
        [
            "Qtr",
            "total_prem",
            "total_claims",
            "hosp_re",
            "total_margin",
            "total_margin_pct",
        ]
    )
)
