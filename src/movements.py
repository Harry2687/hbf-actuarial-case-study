import polars as pl


def check_policy_movements_reconciliation(data: dict) -> dict:
    # Verifies that policy count changes reconcile with the net sum of movements.
    hosp_p = (
        data["policies"]
        .filter(pl.col("Hosp") != "No Hospital Prod")
        .group_by(["Qtr", "Hosp", "Hosp Excess"])
        .agg(pl.col("policies").sum())
        .sort(["Hosp", "Hosp Excess", "Qtr"])
        .with_columns(
            pl.col("policies")
            .diff()
            .over(["Hosp", "Hosp Excess"])
            .alias("policy_change")
        )
    )
    move_hosp_agg = (
        data["movements_hosp"]
        .group_by(["Qtr", "Hosp", "Hosp Excess"])
        .agg(pl.col("Movements").sum().alias("net_movements"))
    )
    hosp_check = (
        hosp_p.join(move_hosp_agg, on=["Qtr", "Hosp", "Hosp Excess"], how="left")
        .filter(pl.col("Qtr") != "2025Q1")
        .with_columns(
            (pl.col("policy_change") - pl.col("net_movements")).alias("discrepancy")
        )
    )

    ext_p = (
        data["policies"]
        .filter(pl.col("Extras") != "No Extras Product")
        .group_by(["Qtr", "Extras"])
        .agg(pl.col("policies").sum())
        .sort(["Extras", "Qtr"])
        .with_columns(pl.col("policies").diff().over("Extras").alias("policy_change"))
    )
    move_ext_agg = (
        data["movements_ext"]
        .group_by(["Qtr", "Extras"])
        .agg(pl.col("Movements").sum().alias("net_movements"))
    )
    ext_check = (
        ext_p.join(move_ext_agg, on=["Qtr", "Extras"], how="left")
        .filter(pl.col("Qtr") != "2025Q1")
        .with_columns(
            (pl.col("policy_change") - pl.col("net_movements")).alias("discrepancy")
        )
    )

    return {
        "hosp_reconciles": hosp_check.filter(pl.col("discrepancy") != 0).height == 0,
        "ext_reconciles": ext_check.filter(pl.col("discrepancy") != 0).height == 0,
    }


def get_hosp_movements_pivot(data: dict) -> pl.DataFrame:
    # Returns a pivoted summary of hospital policy movements by tier.
    return (
        data["movements_hosp"]
        .filter(pl.col("Qtr") != "2025Q1")
        .group_by(["Hosp", "Type"])
        .agg(pl.col("Movements").sum().alias("Total_Movements"))
        .pivot(on="Type", index="Hosp", values="Total_Movements")
        .with_columns(
            [
                (pl.col("Hospital Sale") + pl.col("Hospital Cancellation")).alias(
                    "Net_External"
                ),
                (pl.col("Hosp Move On") + pl.col("Hosp Move Off")).alias(
                    "Net_Internal"
                ),
                (
                    pl.col("Hospital Sale")
                    + pl.col("Hospital Cancellation")
                    + pl.col("Hosp Move On")
                    + pl.col("Hosp Move Off")
                ).alias("Total_Net_Change"),
            ]
        )
        .select(
            [
                "Hosp",
                "Hospital Sale",
                "Hospital Cancellation",
                "Hosp Move On",
                "Hosp Move Off",
                "Net_External",
                "Net_Internal",
                "Total_Net_Change",
            ]
        )
        .sort("Hosp")
    )


def get_ext_movements_pivot(data: dict) -> pl.DataFrame:
    # Returns a pivoted summary of extras policy movements by tier.
    return (
        data["movements_ext"]
        .filter(pl.col("Qtr") != "2025Q1")
        .group_by(["Extras", "Type"])
        .agg(pl.col("Movements").sum().alias("Total_Movements"))
        .pivot(on="Type", index="Extras", values="Total_Movements")
        .with_columns(
            [
                (pl.col("Extras Sale") + pl.col("Extras Cancellation")).alias(
                    "Net_External"
                ),
                (pl.col("Ext Move On") + pl.col("Ext Move Off")).alias("Net_Internal"),
                (
                    pl.col("Extras Sale")
                    + pl.col("Extras Cancellation")
                    + pl.col("Ext Move On")
                    + pl.col("Ext Move Off")
                ).alias("Total_Net_Change"),
            ]
        )
        .select(
            [
                "Extras",
                "Extras Sale",
                "Extras Cancellation",
                "Ext Move On",
                "Ext Move Off",
                "Net_External",
                "Net_Internal",
                "Total_Net_Change",
            ]
        )
        .sort("Extras")
    )
