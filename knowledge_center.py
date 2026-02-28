# knowledge_center.py

# --- KPI DOCUMENTATION ---
KPI_INFO = {
    "gross_demand": """
        **Gross Demand**: The raw AI prediction of customer interest before any deductions. 
        It represents the total potential volume based on historical patterns.
    """,
    "return_rate": """
        **Return Rate (%)**: The estimated percentage of units that will be returned.
        *Formula*: $Net Demand = Gross Demand \\times (1 - Return\\%)$
    """,
    "safety_buffer": """
        **Safety Buffer (%)**: The "Insurance" stock to prevent stockouts due to volatility.
        *Formula*: $Target = Net Demand \\times (1 + Buffer\\%)$
    """
}

# --- MODEL EXPLANATIONS ---
MODEL_MECHANICS = {
    "Prophet": "Uses an additive regression model. It breaks time-series into Trend, Seasonality, and Holidays.",
    "KNN": "Finds 'K' historical days most similar to the target date and uses their average.",
    "Decision Tree": "A supervised learning method that uses a tree-like model of decisions based on seasonality features."
}

# --- SYSTEM INSTRUCTIONS ---
SYSTEM_GUIDE = """
### 🚀 Quick Start Guide
1. **Upload**: Go to 'Data Sources' and upload your Sales CSV.
2. **Clean**: Check the 'Data Integrity' section to ensure dates were parsed correctly.
3. **Tune**: Select an SKU and an Algorithm in 'Model Tuning'.
4. **Simulate**: Adjust sliders for returns and buffers to see the impact on production plans.
"""

# --- DATA REQUIREMENTS ---
CLEANING_PROTOCOLS = """
- **Standardization**: Automatically handles 'Date' vs 'date' vs 'DATE'.
- **Deduplication**: Sums multiple quantities sold on the same day for a single SKU.
- **Safety**: Converts non-numeric sales entries to 0 to prevent model failure.
"""
