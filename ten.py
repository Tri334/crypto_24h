import random
import os
import pandas as pd
from datetime import datetime, timedelta

# ===== Configurable Settings =====
initial_balance = 31.0
months = 100  # Run for 50 months (more reasonable)
trades_per_day = 2  # 1-2 trades per day
risk_percent = 0.10  # 10% risk per trade
max_risk_per_trade = 200.0  # Max risk per trade for 50x leverage
win_rate = 0.55  # Slightly better win rate

# ===== Leverage and Margin Settings =====
initial_leverage = 50
initial_max_margin = 10000  # Max USD position size
upgraded_leverage = 100
upgraded_max_margin = 500000  # Max USD position size

# Calculate actual USD margin required
def calculate_margin_required(position_size, leverage):
    return position_size / leverage
# Random reward ratio between 1.0 and 2.0, with 1.0 being more common
def get_random_reward_ratio():
    # Use beta distribution to make 1.0 more common and 2.0 rare
    # Beta distribution with alpha=2, beta=5 gives more weight to lower values
    return 1.0 + random.betavariate(2, 5)  # This gives values between 1.0 and 2.0
simulations = 3

# ===== Simulation Function with Trade Log =====
def simulate_with_log(sim_id):
    balance = initial_balance
    trade_log = []
    milestone_dates = {}  # No milestones needed for new system
    start_date = datetime.now()
    current_date = start_date
    
    # Initialize leverage and margin settings
    current_leverage = initial_leverage
    current_max_margin = initial_max_margin
    current_max_risk = max_risk_per_trade  # Local copy of max risk
    milestone_reached = False
    
    # Checkpoint tracking
    checkpoint_balance = initial_balance
    max_risk_hit = False
    first_high_risk_hit = False
    high_risk_count = 0
    balance_double_checkpoint = None
    
    # Milestone tracking for leverage 100x
    leverage_125_count = 0
    
    # Track 5th high risk hit and checkpoint
    high_risk_count = 0
    high_risk_checkpoint = None
    doubled_checkpoint_hit = False
    checkpoint_match_flag = False
    
    # Track balance 4000 milestone
    balance_4000_hit = False

    for month_num in range(months):
        days_in_month = 30  # Approximate days per month
        
        for day in range(1, days_in_month + 1):
            # Skip weekends (Saturday = 5, Sunday = 6)
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_date += timedelta(days=1)
                continue
                
            # Random number of trades per day (1-2)
            daily_trades = random.randint(1, trades_per_day)
            
            for trade in range(daily_trades):
                risk_amount = min(balance * risk_percent, current_max_risk)
                outcome = "Win" if random.random() < win_rate else "Loss"
                # Get random reward ratio for this trade
                current_reward_ratio = get_random_reward_ratio()
                # Loss is fixed at 100% of risk amount (ratio = 1.0)
                profit = risk_amount * current_reward_ratio if outcome == "Win" else -risk_amount * 1.1
                balance += profit

                # Calculate actual USD margin required for this position
                actual_margin = calculate_margin_required(risk_amount, current_leverage)
                

                
                # Checkpoint 2: 10% risk from balance hits 200 or more (first time only)
                is_balance_doubled = False
                if risk_amount >= 200 and not first_high_risk_hit:
                    is_balance_doubled = True
                    first_high_risk_hit = True
                
                # Count high risk trades (>= 200)
                if risk_amount >= 200:
                    high_risk_count += 1
                    # Set checkpoint for balance doubling after 5 high risk trades
                    if high_risk_count == 5:
                        balance_double_checkpoint = balance
                
                # Checkpoint 3: Balance doubles from checkpoint after 5 high risk trades
                is_balance_doubled_after_5 = False
                if balance_double_checkpoint and balance >= balance_double_checkpoint * 2:
                    is_balance_doubled_after_5 = True
                
                # Track 5th high risk hit and checkpoint
                is_checkpoint_doubled = False
                if risk_amount >= 200:
                    high_risk_count += 1
                    if high_risk_count == 5:
                        high_risk_checkpoint = balance
                if high_risk_checkpoint and not doubled_checkpoint_hit and balance >= 2 * high_risk_checkpoint:
                    is_checkpoint_doubled = True
                    doubled_checkpoint_hit = True

                # Track 5th high risk hit and checkpoint
                is_checkpoint_match = False
                if risk_amount >= 200:
                    high_risk_count += 1
                    if high_risk_count == 5:
                        high_risk_checkpoint = balance
                # Flag the first row where balance matches the checkpoint
                if high_risk_checkpoint and not checkpoint_match_flag and abs(balance - high_risk_checkpoint) < 1e-6:
                    is_checkpoint_match = True
                    checkpoint_match_flag = True
                
                # Flag the first row where balance hits 4000 or more
                if balance >= 4000 and not balance_4000_hit:
                    is_checkpoint_match = True
                    balance_4000_hit = True

                # Log trade
                trade_log.append({
                    "Date": current_date.strftime("%d/%m/%y"),
                    "Trade": trade + 1,
                    "Leverage": current_leverage,
                    "Outcome": outcome,
                    "Risk_Amount": round(risk_amount, 2),
                    "Profit/Loss": round(profit, 2),
                    "Balance": round(balance, 2)
                })

                # Check for initial milestone ($4000) to upgrade leverage
                if balance >= 4000 and current_leverage == initial_leverage:
                    current_leverage = upgraded_leverage
                    current_max_margin = upgraded_max_margin
                    current_max_risk = 5000.0  # Increase max risk to 5000 for 100x leverage
                
                # Check for leverage 100x milestone (20 times with max position size)
                if current_leverage == upgraded_leverage:
                    leverage_125_count += 1
                    if leverage_125_count >= 20:
                        # Milestone reached - leverage 100x hit 20 times
                        milestone_reached = True
                        break  # Exit the trade loop

            current_date += timedelta(days=1)
            # Exit early if milestone reached
            if milestone_reached:
                break

    df_log = pd.DataFrame(trade_log)
    final_balance = balance
    total_days = len(trade_log) // trades_per_day  # Approximate total days
    years_calc = total_days // 365
    months_calc = (total_days % 365) // 30
    days_calc = total_days % 30
    return df_log, milestone_dates, final_balance, years_calc, months_calc, days_calc

# ===== Run All Simulations =====
summary_records = []
excel_data = {}

for sim in range(1, simulations + 1):
    df_log, milestone_dates, final_balance, years_calc, months_calc, days_calc = simulate_with_log(sim)
    excel_data[f"Sim {sim}"] = df_log
    record = {
        "Simulation": sim, 
        "Final Balance": round(final_balance,2),
        "Years": years_calc,
        "Months": months_calc,
        "Days": days_calc,
        "Total Time": f"{years_calc}y {months_calc}m {days_calc}d"
    }
    summary_records.append(record)

# ===== Create Summary Sheet =====
df_summary = pd.DataFrame(summary_records)
excel_data["Summary"] = df_summary

# ===== Export to Excel with Multiple Sheets =====
excel_path = "simulation_report.xlsx"  # Local path, change as needed
# ✅ Delete the file if it already exists
if os.path.exists(excel_path):
    os.remove(excel_path)
with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
    workbook = writer.book
    
    # Create formats for different checkpoints
    blue_format = workbook.add_format({'bg_color': '#4F81BD', 'font_color': 'white', 'bold': True})  # New month
    green_format = workbook.add_format({'bg_color': '#00FF00', 'font_color': 'black', 'bold': True}) # Checkpoint match
    
    for sheet_name, df in excel_data.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Apply formatting for different checkpoints (only for simulation sheets, not summary)
        if sheet_name != "Summary":
            worksheet = writer.sheets[sheet_name]
            # Track checkpoint for Excel formatting
            high_risk_count_excel = 0
            checkpoint_balance_excel = None
            checkpoint_matched = False
            balance_4000_matched = False
            
            for idx, row in df.iterrows():
                date_str = row['Date']
                risk_amount = row['Risk_Amount']
                leverage = row['Leverage']
                balance = row['Balance']
                
                # Track high risk trades for Excel formatting
                if risk_amount >= 200:
                    high_risk_count_excel += 1
                    if high_risk_count_excel == 5:
                        checkpoint_balance_excel = balance
                
                # Green: Priority 1 - Balance matches checkpoint, Priority 2 - Balance hits 4000
                if checkpoint_balance_excel and not checkpoint_matched and abs(balance - checkpoint_balance_excel) < 1e-6:
                    worksheet.set_row(idx + 1, None, green_format)
                    checkpoint_matched = True
                elif balance >= 4000 and not balance_4000_matched:
                    worksheet.set_row(idx + 1, None, green_format)
                    balance_4000_matched = True
                elif date_str.startswith('01/'):  # Check if it's day 1
                    worksheet.set_row(idx + 1, None, blue_format)

print(f"✅ Excel report saved to: {excel_path}")
