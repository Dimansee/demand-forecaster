# knowledge_center.py

KPI_DEFINITIONS = {
    "Gross Demand": "The raw AI prediction of customer interest before any deductions. It represents the total potential volume.",
    "Return Rate": {
        "Logic": "The estimated percentage of units that will be returned.",
        "Formula": "$NetDemand = GrossDemand \\times (1 - Return\%)$",
        "Value": "Prevents over-manufacturing in high-return categories like Fashion."
    },
    "Trend Surge": {
        "Logic": "A user-driven growth factor.",
        "Values": "1.0 (Neutral), 1.5 (+50% Surge), 0.8 (-20% Decline)."
    },
    "Safety Buffer": {
        "Logic": "The 'Insurance' stock.",
        "Formula": "$Target = NetDemand \\times (1 + Buffer\%)$"
    }
}

MODEL_MECHANICS = {
    "Prophet (Intelligent Demand)": [
        "Uses an additive regression model. It breaks time-series into:",
        "**Trend**: Non-periodic changes.",
        "**Seasonality**: Daily, weekly, and yearly cycles.",
        "**Holidays**: User-defined spikes."
    ],
    "KNN (K-Nearest Neighbors)": "A non-parametric method that finds the 'K' historical days most similar to the target date and uses their average.",
    "Decision Tree": "A supervised learning method that uses a tree-like model of decisions. Excellent for identifying if certain factors (like price or marketing) trigger specific demand levels."
}

MODULE_OVERVIEW = {
    "Data Prep Module": "Cleans date formats, handles null values, and merges disparate files (Marketing, Events, Sales).",
    "Forecast Engine": "A centralized hub that routes your SKU data to the selected math model.",
    "Strategy Overrider": "The layer that takes AI results and applies your manual 'Custom' inputs (Surge, Marketing, Festival Lifts)."
}
