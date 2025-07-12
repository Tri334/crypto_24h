import random
import datetime
from dateutil.relativedelta import relativedelta

# Settings
money = 20.0
max_trade_amount = 5000.0
max_trades_per_month = 10  # ✅ Customizable: max trades allowed per month

# Easy-to-edit simulation range
start_year = 2025
start_month = 1
num_months = 1

# Compute date range
start_date = datetime.date(start_year, start_month, 1)
end_date = start_date + relativedelta(months=num_months) - datetime.timedelta(days=1)

# Track results
day_counter = 0
month_results = {}
current_date = start_date
monthly_trade_count = 0
current_month = start_date.month

while current_date <= end_date:
    if current_date.weekday() < 5:  # Weekday (Mon–Fri)
        # Reset monthly trade count if new month
        if current_date.month != current_month:
            current_month = current_date.month
            monthly_trade_count = 0

        if monthly_trade_count < max_trades_per_month:
            day_counter += 1
            monthly_trade_count += 1
            is_loss = random.random() < (1 / 5)
            trade_amount = min(0.1 * money, max_trade_amount)

            if is_loss:
                money -= (trade_amount * 130/100)
                result = f"LOSS (-${(trade_amount * 130/100):,.2f})"
            else:
                is_multilier = False
                if is_multilier:
                    trade_multiplier = random.choices([0.5,1, 2, 3, 4], weights=[80,50, 15, 5, 2])[0]
                else: trade_multiplier = 1
                trade_amount = trade_amount * trade_multiplier
                money += trade_amount
                result = f"WIN (+${trade_amount:,.2f})"

            print(f"{current_date} | Day {day_counter}: ${money:,.2f} → {result}")

            # Record money at end of month
            month_key = current_date.strftime("%Y-%m")
            month_results[month_key] = money

    current_date += datetime.timedelta(days=1)

# Summary
print("\n📊 Monthly Summary:")
for month, amount in month_results.items():
    print(f"{month}: ${amount:,.2f}")

print(f"\nFinal total money after {num_months} month(s): ${money:,.2f}")
print(f"Salary {num_months} month: {(num_months * 5500000 / 16300):,.2f}")
