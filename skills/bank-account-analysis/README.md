# Bank Account Analysis Skill

Israeli bank account analysis with Hebrew PDF reports.

## Overview

This Claude Code skill analyzes financial data from Israeli bank accounts and credit cards. Users upload Excel/CSV files, and the skill generates a professional Hebrew PDF report with charts and insights.

## Supported Banks

- Bank Hapoalim
- Bank Leumi
- Bank Discount
- Bank Mizrahi-Tefahot
- First International Bank (FIBI)
- Bank Jerusalem / One Zero

## Supported Credit Cards

- Visa Cal
- Isracard
- Max (Leumi Card)

## Analysis Modules

1. **Financial Summary** - Income vs. expenses, average balance
2. **Expense Breakdown** - 15+ Israeli-specific categories
3. **Monthly Trends** - Month-over-month comparison, seasonality
4. **Standing Orders & Subscriptions** - Recurring payment detection
5. **Anomaly Detection** - Unusual expenses flagged
6. **Savings Potential** - Concrete saving opportunities with amounts
7. **Cash Flow Forecast** - 3-month projection
8. **Financial Health Score** - 0-100 score with breakdown

## Python Dependencies

```
pip install reportlab matplotlib python-bidi
```

## Usage

Install this skill into Claude Code:

```bash
npx @open-finance/skills install bank-account-analysis
```

Then ask Claude to analyze your bank statements in Hebrew.
