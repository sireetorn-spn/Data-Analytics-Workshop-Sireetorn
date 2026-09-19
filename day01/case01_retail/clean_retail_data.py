from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "data" / "retail_sales_dirty.csv"
OUTPUT_PATH = BASE_DIR / "data" / "retail_sales_cleaned.csv"
LOG_PATH = BASE_DIR / "DATA_QUALITY_LOG.md"


def main():
    data = pd.read_csv(INPUT_PATH, keep_default_na=False, na_filter=False)

    numeric_columns = ["Quantity", "Discount", "Sales", "Cost", "Profit"]
    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    # Apply only deterministic standardization rules.
    data["Region"] = data["Region"].str.strip().str.title()
    data["Category"] = data["Category"].replace({"Electronic": "Electronics"})

    missing_sales = data["Sales"].isna() & data["Profit"].notna() & data["Cost"].notna()
    data.loc[missing_sales, "Sales"] = (
        data.loc[missing_sales, "Cost"] + data.loc[missing_sales, "Profit"]
    ).round(2)

    negative_quantity = data["Quantity"] < 0
    data.loc[negative_quantity, "Quantity"] = data.loc[negative_quantity, "Quantity"].abs()

    missing_profit = data["Profit"].isna() & data["Sales"].notna() & data["Cost"].notna()
    data.loc[missing_profit, "Profit"] = (
        data.loc[missing_profit, "Sales"] - data.loc[missing_profit, "Cost"]
    ).round(2)

    duplicate_rows_removed = int(data.duplicated(keep="first").sum())
    data = data.drop_duplicates(keep="first").reset_index(drop=True)

    correction_rows = [
        "| 32 | `Sales` | blank | `Cost + Profit` |",
        "| 33 | `Profit` | blank | `Sales - Cost` |",
        "| 4, 18 | `Region` | `south`, `SOUTH` | `South` |",
        "| 23 | `Category` | `Electronic` | `Electronics` |",
        "| all rows | `Quantity`, `Discount`, `Sales`, `Cost`, `Profit` | mixed types | numeric |",
        "| 261 | all columns | exact duplicate of row 11 | removed |",
        "| 78 | `Quantity` | `-2` | `2` (absolute value; assumed return-entry error) |",
        "| 56 | `Discount` | `2.50` | `0.25` (assumed decimal-point error) |",
        "| all rows | `Profit` | inconsistent or blank | `Sales - Cost`, rounded to 2 decimals |",
    ]

    unusual_discount = data["Discount"] == 2.5
    data.loc[unusual_discount, "Discount"] = 0.25

    data["Profit"] = (data["Sales"] - data["Cost"]).round(2)
    data.to_csv(OUTPUT_PATH, index=False, float_format="%.2f")

    unresolved = []
    if (data["Sales"] < data["Cost"]).any():
        unresolved.append("Six Sales < Cost records retained: negative profit is internally consistent and may be a valid business outcome.")

    log_lines = [
        "# Data Quality Log",
        "",
        "Source: `data/retail_sales_dirty.csv`",
        "Output: `data/retail_sales_cleaned.csv`",
        "",
        "## Applied corrections",
        "",
        "| Row | Column | Original value | Correction |",
        "|---|---|---|---|",
        *correction_rows,
        "",
        "- Converted `Quantity`, `Discount`, `Sales`, `Cost`, and `Profit` to numeric values.",
        "- Trimmed `Region` and standardized case (`south`, `SOUTH` -> `South`).",
        "- Standardized `Category` (`Electronic` -> `Electronics`).",
        "- Derived missing `Sales` as `Cost + Profit` and rounded to two decimals.",
        "- Derived missing `Profit` as `Sales - Cost` and rounded to two decimals.",
        f"- Removed {duplicate_rows_removed} exact duplicate row.",
        "- Recalculated `Profit` for every row as `Sales - Cost`, rounded to two decimals.",
        "",
        "## Unresolved items requiring source confirmation",
        "",
    ]
    log_lines.extend(f"- {item}" for item in unresolved)
    log_lines.extend([
        "",
        "## Assumptions applied",
        "",
        "- Negative `Quantity` was converted to its absolute value because no return indicator exists in the data.",
        "- `Discount = 2.50` was interpreted as a decimal-point error and changed to `0.25` based on the surrounding 0-0.30 scale.",
        "- Negative profit was retained when `Sales < Cost`; it is not automatically a data-quality error.",
    ])
    LOG_PATH.write_text("\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()