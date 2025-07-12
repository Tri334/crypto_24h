import random
import pandas as pd
import matplotlib.pyplot as plt

# ===== Configurable Settings =====
initial_balance = 10.0
milestones = [1000, 2000, 5000]
months = 12
max_trades_per_month = 20
risk_percent = 0.10
max_risk_per_trade = 200.0
win_rate = 0.50
reward_ratio = 2.0
simulations = 10

# ===== Simulation Function with Trade Log =====
def simulate_with_log(sim_id):
    balance = initial_balance
    trade_log = []
    milestone_days = {m: None for m in milestones}
    current_day = 1

    for month in range(months):
        trade_dates = sorted(random.sample(range(1, 29), max_trades_per_month))
        for _ in trade_dates:
            risk_amount = min(balance * risk_percent, max_risk_per_trade)
            outcome = "Win" if random.random() < win_rate else "Loss"
            profit = risk_amount * reward_ratio if outcome == "Win" else -risk_amount
            balance += profit

            # Log trade
            trade_log.append({
                "Day": current_day,
                "Outcome": outcome,
                "Profit/Loss": round(profit,2),
                "Balance": round(balance,2)
            })

            for m in milestones:
                if milestone_days[m] is None and balance >= m:
                    milestone_days[m] = current_day

            current_day += 1

    df_log = pd.DataFrame(trade_log)
    final_balance = balance
    return df_log, milestone_days, final_balance

# ===== Run All Simulations =====
summary_records = []
excel_data = {}

for sim in range(1, simulations + 1):
    df_log, milestone_days, final_balance = simulate_with_log(sim)
    excel_data[f"Sim {sim}"] = df_log
    record = {"Simulation": sim, "Final Balance": round(final_balance,2)}
    record.update(milestone_days)
    summary_records.append(record)

# ===== Create Summary Sheet =====
df_summary = pd.DataFrame(summary_records)
excel_data["Summary"] = df_summary

import os
# ===== Export to Excel with Multiple Sheets =====
excel_path = "simulation_report.xlsx"  # Local path, change as needed
# ✅ Delete the file if it already exists
if os.path.exists(excel_path):
    os.remove(excel_path)
with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
    for sheet_name, df in excel_data.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"✅ Excel report saved to: {excel_path}")
