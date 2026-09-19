# Data Quality Log

Source: `data/retail_sales_dirty.csv`
Output: `data/retail_sales_cleaned.csv`

## Applied corrections

| Row | Column | Original value | Correction |
|---|---|---|---|
| 32 | `Sales` | blank | `Cost + Profit` |
| 33 | `Profit` | blank | `Sales - Cost` |
| 4, 18 | `Region` | `south`, `SOUTH` | `South` |
| 23 | `Category` | `Electronic` | `Electronics` |
| all rows | `Quantity`, `Discount`, `Sales`, `Cost`, `Profit` | mixed types | numeric |
| 261 | all columns | exact duplicate of row 11 | removed |
| 78 | `Quantity` | `-2` | `2` (absolute value; assumed return-entry error) |
| 56 | `Discount` | `2.50` | `0.25` (assumed decimal-point error) |
| all rows | `Profit` | inconsistent or blank | `Sales - Cost`, rounded to 2 decimals |

- Converted `Quantity`, `Discount`, `Sales`, `Cost`, and `Profit` to numeric values.
- Trimmed `Region` and standardized case (`south`, `SOUTH` -> `South`).
- Standardized `Category` (`Electronic` -> `Electronics`).
- Derived missing `Sales` as `Cost + Profit` and rounded to two decimals.
- Derived missing `Profit` as `Sales - Cost` and rounded to two decimals.
- Removed 1 exact duplicate row.
- Recalculated `Profit` for every row as `Sales - Cost`, rounded to two decimals.

## Unresolved items requiring source confirmation

- Six Sales < Cost records retained: negative profit is internally consistent and may be a valid business outcome.

## Assumptions applied

- Negative `Quantity` was converted to its absolute value because no return indicator exists in the data.
- `Discount = 2.50` was interpreted as a decimal-point error and changed to `0.25` based on the surrounding 0-0.30 scale.
- Negative profit was retained when `Sales < Cost`; it is not automatically a data-quality error.
