import polars as pl
import os


def load_sheet(excel_path: str, sheet_name: str) -> pl.DataFrame:
    # Loads a sheet and drops documentation columns.
    df = pl.read_excel(excel_path, sheet_name=sheet_name)
    return df.select(
        [
            c
            for c in df.columns
            if not (c.startswith("FIELDS:") or c.startswith("Description") or c == "")
        ]
    )


def get_cleaned_data(excel_path: str = "202503 HBF Case Study VALUES 1.xlsx") -> dict:
    # Loads and cleans all datasets, normalizing columns and types.
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found at {excel_path}")

    data = {
        "policies": load_sheet(excel_path, "DATA_policies"),
        "hosp_claims": load_sheet(excel_path, "DATA_hosp_claims"),
        "ext_claims": load_sheet(excel_path, "DATA_ext_claims"),
        "re_data": load_sheet(excel_path, "DATA_RE"),
        "movements_hosp": load_sheet(excel_path, "DATA_product_movements_hosp"),
        "movements_ext": load_sheet(excel_path, "DATA_product_movements_ext"),
    }

    for k in ["policies", "hosp_claims", "re_data", "movements_hosp"]:
        data[k] = data[k].with_columns(
            pl.col("Hosp Excess").cast(pl.Int64, strict=False)
        )

    return data
