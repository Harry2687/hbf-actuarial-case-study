import polars as pl


def calculate_hospital_financials(data: dict) -> pl.DataFrame:
    # Computes financial summaries and actuarial metrics for Hospital products.
    hosp_p = (
        data["policies"]
        .filter(pl.col("Hosp") != "No Hospital Prod")
        .group_by(["Qtr", "Hosp", "Hosp Excess"])
        .agg(
            [
                pl.col("hospital_income").sum().alias("premiums"),
                pl.col("policies").sum().alias("policies"),
            ]
        )
    )

    hosp_c = (
        data["hosp_claims"]
        .group_by(["Qtr", "Hosp", "Hosp Excess"])
        .agg(
            [
                pl.col("TOTAL_BENEFIT").sum().alias("claims"),
                pl.col("TOTAL_FEES_CHARGED").sum().alias("fees_charged"),
                pl.col("BED_DAYS").sum().alias("bed_days"),
                pl.col("Episodes").sum().alias("episodes"),
            ]
        )
    )

    joined = (
        hosp_p.join(hosp_c, on=["Qtr", "Hosp", "Hosp Excess"], how="left")
        .join(data["re_data"], on=["Qtr", "Hosp", "Hosp Excess"], how="left")
        .fill_null(0.0)
        .with_columns(
            (pl.col("premiums") - pl.col("claims") + pl.col("RE Received")).alias(
                "margin"
            )
        )
    )

    return (
        joined.group_by(["Hosp", "Hosp Excess"])
        .agg(
            [
                pl.col("premiums").sum().alias("total_premiums"),
                pl.col("claims").sum().alias("total_claims"),
                pl.col("RE Received").sum().alias("total_re"),
                pl.col("margin").sum().alias("total_margin"),
                pl.col("policies").mean().alias("avg_policies"),
                pl.col("policies")
                .filter(pl.col("Qtr") == "2025Q1")
                .first()
                .alias("policies_start"),
                pl.col("policies")
                .filter(pl.col("Qtr") == "2026Q4")
                .first()
                .alias("policies_end"),
                pl.col("episodes").sum().alias("total_episodes"),
                pl.col("bed_days").sum().alias("total_bed_days"),
            ]
        )
        .with_columns(
            [
                (pl.col("total_claims") / pl.col("total_premiums")).alias(
                    "gross_loss_ratio"
                ),
                (
                    (pl.col("total_claims") - pl.col("total_re"))
                    / pl.col("total_premiums")
                ).alias("net_loss_ratio"),
                (pl.col("total_margin") / pl.col("total_premiums")).alias("margin_pct"),
                (pl.col("total_premiums") / (pl.col("avg_policies") * 8)).alias(
                    "qtr_premium_per_policy"
                ),
                (pl.col("total_episodes") / (pl.col("avg_policies") * 8)).alias(
                    "qtr_freq_per_policy"
                ),
                (pl.col("total_claims") / pl.col("total_episodes")).alias(
                    "severity_per_episode"
                ),
                (pl.col("total_bed_days") / pl.col("total_episodes")).alias(
                    "bed_days_per_episode"
                ),
                (pl.col("total_margin") / (pl.col("avg_policies") * 8)).alias(
                    "qtr_margin_per_policy"
                ),
                (
                    (pl.col("policies_end") - pl.col("policies_start"))
                    / pl.col("policies_start")
                ).alias("policy_growth_pct"),
                (pl.col("total_re") / (pl.col("avg_policies") * 8)).alias(
                    "qtr_re_per_policy"
                ),
            ]
        )
        .with_columns(
            [
                pl.col("total_premiums").round(2),
                pl.col("total_claims").round(2),
                pl.col("total_re").round(2),
                pl.col("total_margin").round(2),
                pl.col("avg_policies").round(2),
                pl.col("policies_start").cast(pl.Int64),
                pl.col("policies_end").cast(pl.Int64),
                pl.col("total_episodes").cast(pl.Int64),
                pl.col("total_bed_days").cast(pl.Int64),
                pl.col("gross_loss_ratio").round(4),
                pl.col("net_loss_ratio").round(4),
                pl.col("margin_pct").round(4),
                pl.col("qtr_premium_per_policy").round(2),
                pl.col("qtr_freq_per_policy").round(4),
                pl.col("severity_per_episode").round(2),
                pl.col("bed_days_per_episode").round(2),
                pl.col("qtr_margin_per_policy").round(2),
                pl.col("policy_growth_pct").round(4),
                pl.col("qtr_re_per_policy").round(2),
            ]
        )
        .sort(["Hosp", "Hosp Excess"])
    )


def calculate_extras_financials(data: dict) -> pl.DataFrame:
    # Computes financial summaries and actuarial metrics for Extras products.
    ext_p = (
        data["policies"]
        .filter(pl.col("Extras") != "No Extras Product")
        .group_by(["Qtr", "Extras"])
        .agg(
            [
                pl.col("extras_income").sum().alias("premiums"),
                pl.col("policies").sum().alias("policies"),
            ]
        )
    )

    ext_c = (
        data["ext_claims"]
        .group_by(["Qtr", "Extras"])
        .agg(
            [
                pl.col("TOTAL_BENEFIT").sum().alias("claims"),
                pl.col("TOTAL_FEES_CHARGED").sum().alias("fees_charged"),
                pl.col("TOTAL_SERVICES").sum().alias("services"),
            ]
        )
    )

    joined = (
        ext_p.join(ext_c, on=["Qtr", "Extras"], how="left")
        .fill_null(0.0)
        .with_columns((pl.col("premiums") - pl.col("claims")).alias("margin"))
    )

    return (
        joined.group_by("Extras")
        .agg(
            [
                pl.col("premiums").sum().alias("total_premiums"),
                pl.col("claims").sum().alias("total_claims"),
                pl.col("margin").sum().alias("total_margin"),
                pl.col("policies").mean().alias("avg_policies"),
                pl.col("policies")
                .filter(pl.col("Qtr") == "2025Q1")
                .first()
                .alias("policies_start"),
                pl.col("policies")
                .filter(pl.col("Qtr") == "2026Q4")
                .first()
                .alias("policies_end"),
                pl.col("services").sum().alias("total_services"),
            ]
        )
        .with_columns(
            [
                (pl.col("total_claims") / pl.col("total_premiums")).alias("loss_ratio"),
                (pl.col("total_margin") / pl.col("total_premiums")).alias("margin_pct"),
                (pl.col("total_premiums") / (pl.col("avg_policies") * 8)).alias(
                    "qtr_premium_per_policy"
                ),
                (pl.col("total_services") / (pl.col("avg_policies") * 8)).alias(
                    "qtr_services_per_policy"
                ),
                (pl.col("total_claims") / pl.col("total_services")).alias(
                    "severity_per_service"
                ),
                (pl.col("total_margin") / (pl.col("avg_policies") * 8)).alias(
                    "qtr_margin_per_policy"
                ),
                (
                    (pl.col("policies_end") - pl.col("policies_start"))
                    / pl.col("policies_start")
                ).alias("policy_growth_pct"),
            ]
        )
        .with_columns(
            [
                pl.col("total_premiums").round(2),
                pl.col("total_claims").round(2),
                pl.col("total_margin").round(2),
                pl.col("avg_policies").round(2),
                pl.col("policies_start").cast(pl.Int64),
                pl.col("policies_end").cast(pl.Int64),
                pl.col("total_services").cast(pl.Int64),
                pl.col("loss_ratio").round(4),
                pl.col("margin_pct").round(4),
                pl.col("qtr_premium_per_policy").round(2),
                pl.col("qtr_services_per_policy").round(4),
                pl.col("severity_per_service").round(2),
                pl.col("qtr_margin_per_policy").round(2),
                pl.col("policy_growth_pct").round(4),
            ]
        )
        .sort("Extras")
    )
