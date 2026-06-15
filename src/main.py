import os
import polars as pl
from src.loader import get_cleaned_data
from src.financials import calculate_hospital_financials, calculate_extras_financials
from src.movements import (
    check_policy_movements_reconciliation,
    get_hosp_movements_pivot,
    get_ext_movements_pivot,
)
from src.clinical import (
    get_top_hospital_categories,
    get_extras_categories,
    get_silver_vs_gold_psychiatry,
    get_claims_seasonality,
)


def main():
    # Pipeline runner that executes all steps and saves outputs to 'analysis_output/' directory.
    print("Running HBF Actuarial Pipeline...")
    data = get_cleaned_data("202503 HBF Case Study VALUES 1.xlsx")
    out = "analysis_output"
    os.makedirs(out, exist_ok=True)

    hosp_fin = calculate_hospital_financials(data)
    ext_fin = calculate_extras_financials(data)
    hosp_fin.write_csv(os.path.join(out, "hospital_actuarial_summary.csv"))
    ext_fin.write_csv(os.path.join(out, "extras_actuarial_summary.csv"))

    recon = check_policy_movements_reconciliation(data)
    print(
        f"Reconciled | Hospital: {recon['hosp_reconciles']} | Extras: {recon['ext_reconciles']}"
    )

    hosp_mov = get_hosp_movements_pivot(data)
    ext_mov = get_ext_movements_pivot(data)
    hosp_mov.write_csv(os.path.join(out, "hospital_movements_pivot.csv"))
    ext_mov.write_csv(os.path.join(out, "extras_movements_pivot.csv"))

    get_top_hospital_categories(data).write_csv(
        os.path.join(out, "top_hospital_claim_categories.csv")
    )
    get_extras_categories(data).write_csv(
        os.path.join(out, "top_extras_claim_categories.csv")
    )

    psych = get_silver_vs_gold_psychiatry(data)
    psych["silver_0"].write_csv(os.path.join(out, "silver_0_claim_mix.csv"))
    psych["gold_0"].write_csv(os.path.join(out, "gold_0_claim_mix.csv"))

    get_claims_seasonality(data).write_csv(os.path.join(out, "claims_seasonality.csv"))

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
        .with_columns(
            [
                pl.col("hosp_prem").round(2),
                pl.col("hosp_claims").round(2),
                pl.col("hosp_re").round(2),
                pl.col("hosp_margin").round(2),
                pl.col("ext_prem").round(2),
                pl.col("ext_claims").round(2),
                pl.col("ext_margin").round(2),
                pl.col("total_prem").round(2),
                pl.col("total_claims").round(2),
                pl.col("total_margin").round(2),
                pl.col("total_margin_pct").round(4),
            ]
        )
        .sort("Qtr")
    )
    hbf_total.write_csv(os.path.join(out, "hbf_total_margins.csv"))

    print("\n--- Pipeline Outputs Saved to 'analysis_output/' directory ---")
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


if __name__ == "__main__":
    main()
