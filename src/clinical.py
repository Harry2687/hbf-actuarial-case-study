import polars as pl


def get_top_hospital_categories(data: dict) -> pl.DataFrame:
    # Ranks hospital clinical claim categories by total benefits paid.
    return (
        data["hosp_claims"]
        .group_by("CLAIM_CATEGORY")
        .agg(
            [
                pl.col("TOTAL_BENEFIT").sum().alias("claims"),
                pl.col("Episodes").sum().alias("episodes"),
                pl.col("BED_DAYS").sum().alias("bed_days"),
            ]
        )
        .with_columns(
            [
                (pl.col("claims") / pl.col("claims").sum()).alias("share"),
                (pl.col("claims") / pl.col("episodes")).alias(
                    "avg_benefit_per_episode"
                ),
            ]
        )
        .with_columns(
            [
                pl.col("claims").round(2),
                pl.col("episodes").cast(pl.Int64),
                pl.col("bed_days").cast(pl.Int64),
                pl.col("share").round(4),
                pl.col("avg_benefit_per_episode").round(2),
            ]
        )
        .sort("claims", descending=True)
    )


def get_extras_categories(data: dict) -> pl.DataFrame:
    # Ranks extras claim categories by total benefits paid.
    return (
        data["ext_claims"]
        .group_by("CLAIM_CATEGORY")
        .agg(
            [
                pl.col("TOTAL_BENEFIT").sum().alias("claims"),
                pl.col("TOTAL_SERVICES").sum().alias("services"),
            ]
        )
        .with_columns(
            [
                (pl.col("claims") / pl.col("claims").sum()).alias("share"),
                (pl.col("claims") / pl.col("services")).alias(
                    "avg_benefit_per_service"
                ),
            ]
        )
        .with_columns(
            [
                pl.col("claims").round(2),
                pl.col("services").cast(pl.Int64),
                pl.col("share").round(4),
                pl.col("avg_benefit_per_service").round(2),
            ]
        )
        .sort("claims", descending=True)
    )


def get_silver_vs_gold_psychiatry(data: dict) -> dict:
    # Composes clinical category profiles for Silver 0 and Gold 0 products.
    def get_mix(hosp, excess):
        return (
            data["hosp_claims"]
            .filter((pl.col("Hosp") == hosp) & (pl.col("Hosp Excess") == excess))
            .group_by("CLAIM_CATEGORY")
            .agg(
                [
                    pl.col("TOTAL_BENEFIT").sum().alias("claims"),
                    pl.col("Episodes").sum().alias("episodes"),
                    pl.col("BED_DAYS").sum().alias("bed_days"),
                ]
            )
            .with_columns((pl.col("claims") / pl.col("claims").sum()).alias("share"))
            .with_columns(
                [
                    pl.col("claims").round(2),
                    pl.col("episodes").cast(pl.Int64),
                    pl.col("bed_days").cast(pl.Int64),
                    pl.col("share").round(4),
                ]
            )
            .sort("claims", descending=True)
        )

    return {"silver_0": get_mix("Silver", 0), "gold_0": get_mix("Gold", 0)}


def get_claims_seasonality(data: dict) -> pl.DataFrame:
    # Calculates quarterly claims seasonality for both Hospital and Extras.
    h = (
        data["hosp_claims"]
        .group_by("Qtr")
        .agg(pl.col("TOTAL_BENEFIT").sum().alias("hosp_claims"))
    )
    e = (
        data["ext_claims"]
        .group_by("Qtr")
        .agg(pl.col("TOTAL_BENEFIT").sum().alias("ext_claims"))
    )
    return (
        h.join(e, on="Qtr")
        .with_columns(
            [
                pl.col("hosp_claims").round(2),
                pl.col("ext_claims").round(2),
            ]
        )
        .sort("Qtr")
    )
