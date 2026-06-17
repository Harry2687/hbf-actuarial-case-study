import os
import altair as alt
import polars as pl

def set_hbf_theme():
    """Defines the HBF brand theme for Altair charts."""
    font = "Inter, sans-serif"
    electric_blue = "#90E3E9"
    background = "transparent"

    @alt.theme.register("hbf_theme", enable=True)
    def theme():
        return {
            "config": {
                "autosize": {"type": "fit", "contains": "padding"},
                "background": background,
                "title": {
                    "color": electric_blue,
                    "font": font,
                    "fontSize": 20,
                    "anchor": "middle",
                    "offset": 15
                },
                "axis": {
                    "labelColor": electric_blue,
                    "titleColor": electric_blue,
                    "labelFont": font,
                    "titleFont": font,
                    "gridColor": "rgba(144, 227, 233, 0.1)",
                    "domainColor": electric_blue,
                    "tickColor": electric_blue,
                },
                "legend": {
                    "labelColor": electric_blue,
                    "titleColor": electric_blue,
                    "labelFont": font,
                    "titleFont": font,
                },
                "view": {
                    "stroke": "transparent",
                },
                "text": {
                    "font": font,
                    "color": electric_blue
                }
            }
        }
    

def generate_visualizations(out_dir="analysis_output", public_dir="presentation/public"):
    """Generates visualizations and saves them to the presentation public folder."""
    os.makedirs(public_dir, exist_ok=True)
    set_hbf_theme()
    
    # Base configuration for dynamic sizing
    props = {"width": "container", "height": 320}

    # --- Chart 1: Extras Seasonality Line Chart (Slide 6) ---
    seasonality = pl.read_csv(os.path.join(out_dir, "claims_seasonality.csv"))
    
    chart1 = alt.Chart(seasonality).mark_line(
        color="#91D3D0", strokeWidth=4, point=alt.OverlayMarkDef(color="#90E3E9", size=100)
    ).encode(
        x=alt.X('Qtr:O', title="Quarter", axis=alt.Axis(labelAngle=0)),
        y=alt.Y('ext_claims:Q', title="Total Benefits Paid ($)", axis=alt.Axis(format='$,.0f')),
        tooltip=[alt.Tooltip('Qtr', title='Quarter'), alt.Tooltip('ext_claims', title='Benefits ($)', format='$,.0f')]
    ).properties(title="Extras Claim Seasonality (Quarterly)", **props).interactive()
    
    chart1.save(os.path.join(public_dir, "seasonality.html"))

    # --- Chart 2: Product Trajectories (Slide 3) ---
    hosp = pl.read_csv(os.path.join(out_dir, "hospital_actuarial_summary.csv"))
    ext = pl.read_csv(os.path.join(out_dir, "extras_actuarial_summary.csv"))
    
    hosp_growth = hosp.group_by("Hosp").agg([
        pl.col("policies_start").sum(),
        pl.col("policies_end").sum()
    ]).with_columns(
        Product=pl.col("Hosp") + " Hospital",
        Growth=(pl.col("policies_end") - pl.col("policies_start")) / pl.col("policies_start")
    )
    ext_growth = ext.with_columns(
        Product=pl.col("Extras") + " Extras",
        Growth=(pl.col("policies_end") - pl.col("policies_start")) / pl.col("policies_start")
    ).select(["Product", "Growth"])
    
    growth_df = pl.concat([hosp_growth.select(["Product", "Growth"]), ext_growth])
    chart2 = alt.Chart(growth_df).mark_bar().encode(
        x=alt.X('Growth:Q', title="Growth (%)", axis=alt.Axis(format='%')),
        y=alt.Y('Product:N', sort='-x', title=None),
        color=alt.condition(
            alt.datum.Growth > 0,
            alt.value("#91D3D0"),  # Positive
            alt.value("#ff6b6b")   # Negative
        ),
        tooltip=[alt.Tooltip('Product'), alt.Tooltip('Growth', format='.1%')]
    ).properties(title="Product Trajectories (Growth 2025-2026)", **props).interactive()
    
    chart2.save(os.path.join(public_dir, "trajectories.html"))
    
    # --- Chart 3: Silver 0 Psychiatry Anomaly (Slide 5) ---
    silver_mix = pl.read_csv(os.path.join(out_dir, "silver_0_claim_mix.csv")).head(5)
    
    chart3 = alt.Chart(silver_mix).mark_arc(innerRadius=60, stroke="#01395A", strokeWidth=2).encode(
        theta=alt.Theta(field="claims", type="quantitative"),
        color=alt.Color(field="CLAIM_CATEGORY", type="nominal", 
                        sort=alt.EncodingSortField(field="claims", order="descending"),
                        scale=alt.Scale(range=["#ff6b6b", "#90E3E9", "#91D3D0", "#fbc531", "#ffffff"]),
                        legend=alt.Legend(title=None, orient="bottom", labelLimit=300)),
        tooltip=[alt.Tooltip('CLAIM_CATEGORY', title='Category'), 
                 alt.Tooltip('claims', title='Benefits ($)', format='$,.0f'),
                 alt.Tooltip('share', title='Share', format='.1%')]
    ).properties(title=alt.TitleParams("Silver 0 Claims by Category", anchor="start"), **props).interactive()
    
    chart3.save(os.path.join(public_dir, "silver_0_mix.html"))

    # --- Chart 4: Profitability by Segment (Slide 3) ---
    hosp_prof = hosp.group_by("Hosp").agg(
        MarginPerPolicy=(pl.col("total_margin").sum() / pl.col("avg_policies").sum())
    ).with_columns(Product=pl.col("Hosp") + " Hospital")
    
    ext_prof = ext.group_by("Extras").agg(
        MarginPerPolicy=(pl.col("total_margin").sum() / pl.col("avg_policies").sum())
    ).with_columns(Product=pl.col("Extras") + " Extras")
    
    prof_df = pl.concat([hosp_prof.select(["Product", "MarginPerPolicy"]), ext_prof.select(["Product", "MarginPerPolicy"])])
    
    chart4 = alt.Chart(prof_df).mark_bar().encode(
        x=alt.X('MarginPerPolicy:Q', title="Total 2-Year Net Margin per Policy ($)", axis=alt.Axis(format='$,.0f')),
        y=alt.Y('Product:N', sort='-x', title=None),
        color=alt.condition(alt.datum.MarginPerPolicy > 0, alt.value("#91D3D0"), alt.value("#ff6b6b")),
        tooltip=[alt.Tooltip('Product'), alt.Tooltip('MarginPerPolicy', format='$,.2f', title="Margin/Policy")]
    ).properties(title="Profitability by Segment", **props).interactive()
    
    chart4.save(os.path.join(public_dir, "profitability.html"))

    # --- Chart 5: Total Risk Equalisation Transfers (Slide 6) ---
    re_transfers = hosp.group_by("Hosp").agg(
        pl.col("total_re").sum().alias("Total RE Transfer ($)")
    ).with_columns(Tier=pl.col("Hosp"))
    
    chart5 = alt.Chart(re_transfers).mark_bar().encode(
        x=alt.X('Tier:N', title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Total RE Transfer ($):Q', axis=alt.Axis(format='$,.0f'), title="Net RE Transfer ($)"),
        color=alt.condition(alt.datum['Total RE Transfer ($)'] > 0, alt.value("#91D3D0"), alt.value("#ff6b6b")),
        tooltip=[alt.Tooltip('Tier:N'), alt.Tooltip('Total RE Transfer ($):Q', format='$,.0f')]
    ).properties(title="Total Risk Equalisation Transfers", **props).interactive()

    chart5.save(os.path.join(public_dir, "re_reversal.html"))

    # --- Chart 6: Membership Attrition (Slide 5) ---
    hosp_mov = pl.read_csv(os.path.join(out_dir, "hospital_movements_pivot.csv"))
    attrition_data = hosp_mov.select([
        pl.col("Hosp").alias("Tier"),
        pl.col("Net_External").alias("External"), 
        pl.col("Net_Internal").alias("Internal")
    ])
    
    chart6 = alt.Chart(attrition_data).transform_fold(
        ['External', 'Internal'], as_=['Type', 'Members']
    ).mark_bar().encode(
        x=alt.X('Type:N', title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Members:Q', title="Net Change in Policies"),
        column=alt.Column('Tier:N', title=None),
        color=alt.Color('Type:N', scale=alt.Scale(range=["#ff6b6b", "#fbc531"])),
        tooltip=[alt.Tooltip('Tier:N'), alt.Tooltip('Type:N'), alt.Tooltip('Members:Q')]
    ).properties(title="Hospital Policy Movements (2025-2026)", width=120, height=280).interactive()
    
    chart6.save(os.path.join(public_dir, "attrition.html"))

    print("Dynamic Visualizations successfully generated into presentation/public/")

    for f in os.listdir(public_dir):
        if f.endswith(".html"):
            path = os.path.join(public_dir, f)
            with open(path, "r") as file:
                content = file.read()
            if "html, body {" not in content:
                content = content.replace("</style>", "html, body { width: 100%; margin: 0; padding: 0; overflow: hidden; }\n</style>")
                with open(path, "w") as file:
                    file.write(content)
