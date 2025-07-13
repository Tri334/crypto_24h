"""
Crypto Futures Trading Simulation - Upgraded Version
==================================================

A comprehensive simulation of crypto futures trading with:
- Dynamic leverage progression (50x → 100x)
- Risk management with variable limits
- Milestone tracking and visual indicators
- Weekend trading restrictions
- Realistic profit/loss calculations

Author: AI Assistant
Version: 2.0
"""

import random
import os
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TradingConfig:
    """Configuration class for trading parameters"""
    initial_balance: float = 31.0
    months: int = 100
    trades_per_day: int = 2
    risk_percent: float = 0.10
    win_rate: float = 0.58
    simulations: int = 3
    max_months: int = 12  # Maximum months to run simulation (5 years)

@dataclass
class LeverageConfig:
    """Configuration class for leverage settings"""
    initial_leverage: int = 10
    initial_max_margin: int = 10000
    upgraded_leverage: int = 100
    upgraded_max_margin: int = 500000
    initial_max_risk: float = 200.0
    upgraded_max_risk: float = 5000.0
    upgrade_threshold: float = 4000.0

@dataclass
class MilestoneConfig:
    """Configuration class for milestone tracking"""
    high_risk_threshold: float = 200.0
    checkpoint_trades: int = 5
    leverage_milestone_trades: int = 20
    final_balance_target: float = 500000.0  # Final milestone: $500,000 USD

@dataclass
class BackupConfig:
    """Configuration class for backup strategy"""
    backup_activation_threshold: float = 4000.0  # When balance hits this, create backup
    backup_amount: float = 1500.0  # Amount to take as backup
    max_backup: float = 1500.0  # Maximum backup amount
    recovery_threshold: float = 1500.0  # When balance hits this, use all backup



class TradingSimulator:
    """Main trading simulation class"""
    
    def __init__(self, trading_config: TradingConfig, leverage_config: LeverageConfig, milestone_config: MilestoneConfig, backup_config: BackupConfig):
        self.trading_config = trading_config
        self.leverage_config = leverage_config
        self.milestone_config = milestone_config
        self.backup_config = backup_config
        
    def calculate_margin_required(self, position_size: float, leverage: int) -> float:
        """Calculate actual USD margin required for a position"""
        return position_size / leverage
    
    def get_random_reward_ratio(self) -> float:
        """Generate random reward ratio between 1.0 and 2.0 using beta distribution"""
        return 1.0 + random.betavariate(2, 5)
    
    def is_weekend(self, date: datetime) -> bool:
        """Check if the given date is a weekend"""
        return date.weekday() >= 5
    
    def calculate_profit_loss(self, risk_amount: float, outcome: str, reward_ratio: float) -> float:
        """Calculate profit/loss for a trade"""
        if outcome == "Win":
            return risk_amount * reward_ratio * 0.9  # Profit reduced by 10%
        else:
            return -risk_amount * 1.1  # Loss with 10% additional cost
    
    def should_upgrade_leverage(self, balance: float, current_leverage: int) -> bool:
        """Check if leverage should be upgraded"""
        return balance >= self.leverage_config.upgrade_threshold and current_leverage == self.leverage_config.initial_leverage
    
    def upgrade_leverage_settings(self, current_leverage: int, current_max_margin: int, current_max_risk: float) -> Tuple[int, int, float]:
        """Upgrade leverage settings when threshold is reached"""
        return (
            self.leverage_config.upgraded_leverage,
            self.leverage_config.upgraded_max_margin,
            self.leverage_config.upgraded_max_risk
        )
    
    def create_trade_record(self, current_date: datetime, trade_num: int, leverage: int, 
                          outcome: str, risk_amount: float, profit_loss: float, balance: float, backup_funds: float) -> Dict:
        """Create a standardized trade record"""
        return {
            "Date": current_date.strftime("%d/%m/%y"),
            "Trade": trade_num,
            "Leverage": leverage,
            "Outcome": outcome,
            "Risk_Amount": round(risk_amount, 2),
            "Profit/Loss": round(profit_loss, 2),
            "Balance": round(balance, 2),
            "Backup_Balance": round(backup_funds, 2)
        }
    
    def simulate_trading_session(self, sim_id: int) -> Tuple[pd.DataFrame, Dict, float, datetime, datetime]:
        """Run a complete trading simulation"""
        logger.info(f"Starting simulation {sim_id}")
        
        # Initialize simulation state
        balance = self.trading_config.initial_balance
        trade_log = []
        milestone_dates = {}
        start_date = datetime.now()
        current_date = start_date
        first_trade_date = None
        last_trade_date = None
        
        # Trading state
        current_leverage = self.leverage_config.initial_leverage
        current_max_margin = self.leverage_config.initial_max_margin
        current_max_risk = self.leverage_config.initial_max_risk
        milestone_reached = False
        
        # Milestone tracking
        high_risk_count = 0
        high_risk_checkpoint = None
        checkpoint_match_flag = False
        balance_4000_hit = False
        leverage_upgrade_count = 0
        
        # Backup strategy tracking
        backup_funds = 0.0
        backup_created = False
        

        
        # Run simulation until final milestone is reached or max months limit
        month_count = 0
        while balance < self.milestone_config.final_balance_target and month_count < self.trading_config.max_months:
            # Simulate one month
            month_count += 1
            for day in range(1, 31):  # 30 days per month
                # Skip weekends
                if self.is_weekend(current_date):
                    current_date += timedelta(days=1)
                    continue
                
                # Daily trading - reduce to 1 trade per day when using 100x leverage
                if current_leverage == self.leverage_config.upgraded_leverage:
                    daily_trades = 1
                else:
                    daily_trades = random.randint(1, self.trading_config.trades_per_day)
                
                for trade in range(daily_trades):
                    # Calculate trade parameters
                    risk_amount = min(balance * self.trading_config.risk_percent, current_max_risk)
                    outcome = "Win" if random.random() < self.trading_config.win_rate else "Loss"
                    # Use static profit for 100x leverage
                    if current_leverage == self.leverage_config.upgraded_leverage:
                        reward_ratio = 1.0
                    else:
                        reward_ratio = self.get_random_reward_ratio()
                    profit_loss = self.calculate_profit_loss(risk_amount, outcome, reward_ratio)
                    balance += profit_loss
                    
                    # Apply backup strategy
                    balance, backup_funds, backup_created = self._apply_backup_strategy(balance, backup_funds, backup_created)
                    
                    # Track milestones
                    self._track_milestones(risk_amount, balance, high_risk_count, high_risk_checkpoint, 
                                         checkpoint_match_flag, balance_4000_hit)
                    
                    # Track first and last trade dates
                    if first_trade_date is None:
                        first_trade_date = current_date
                    last_trade_date = current_date
                    
                    # Log trade
                    trade_record = self.create_trade_record(
                        current_date, trade + 1, current_leverage, outcome, 
                        risk_amount, profit_loss, balance, backup_funds
                    )
                    trade_log.append(trade_record)
                    
                    # Check for leverage upgrade
                    if self.should_upgrade_leverage(balance, current_leverage):
                        current_leverage, current_max_margin, current_max_risk = self.upgrade_leverage_settings(
                            current_leverage, current_max_margin, current_max_risk
                        )
                        logger.info(f"Leverage upgraded to {current_leverage}x at balance ${balance:.2f}")
                    
                    # Check for final milestone ($500,000) - HIGHEST PRIORITY
                    if balance >= self.milestone_config.final_balance_target:
                        milestone_reached = True
                        logger.info(f"🎉 FINAL MILESTONE REACHED: ${balance:,.2f} USD!")
                        break
                    # Check for leverage milestone (20 trades with upgraded leverage) - SECONDARY
                    elif current_leverage == self.leverage_config.upgraded_leverage:
                        leverage_upgrade_count += 1
                        if leverage_upgrade_count >= self.milestone_config.leverage_milestone_trades:
                            logger.info(f"Leverage milestone reached after {leverage_upgrade_count} trades with {current_leverage}x leverage - continuing to $500k...")
                            # Don't set milestone_reached = True, continue trading
                            leverage_upgrade_count = 0  # Reset counter to continue tracking
                
                current_date += timedelta(days=1)
                
                if milestone_reached:
                    break
            
            if milestone_reached:
                break
        
        # Calculate time metrics based on actual trade dates
        if first_trade_date and last_trade_date:
            total_duration = last_trade_date - first_trade_date
            total_days = total_duration.days
            years_calc = total_days // 365
            months_calc = (total_days % 365) // 30
            days_calc = total_days % 30
        else:
            years_calc = months_calc = days_calc = 0
        
        # Add safety check for very long simulations
        if total_days > 365 * 50:  # More than 50 years
            logger.warning(f"Simulation {sim_id} took {years_calc} years - very long duration!")
        
        # Check if simulation hit month limit
        if month_count >= self.trading_config.max_months and balance < self.milestone_config.final_balance_target:
            logger.warning(f"Simulation {sim_id} hit {self.trading_config.max_months}-month time limit! Final balance: ${balance:.2f}")
        
        logger.info(f"Simulation {sim_id} completed: Final balance ${balance:.2f}, Duration: {years_calc}y {months_calc}m {days_calc}d")
        
        return pd.DataFrame(trade_log), milestone_dates, balance, first_trade_date, last_trade_date
    
    def _apply_backup_strategy(self, balance: float, backup_funds: float, backup_created: bool) -> Tuple[float, float, bool]:
        """Apply backup strategy: pour backup at 1500, create backup at 4000"""
        
        # Recovery: when balance hits 1500, pour all backup
        if balance >= self.backup_config.recovery_threshold and backup_funds > 0:
            recovery_amount = backup_funds
            backup_funds = 0.0
            balance += recovery_amount
            logger.info(f"🆘 Recovery: Balance hit ${self.backup_config.recovery_threshold:.0f}! Added ${recovery_amount:.2f} from backup → Balance ${balance:.2f}")
        
        # Create backup when balance hits 4000
        if balance >= self.backup_config.backup_activation_threshold:
            backup_amount = min(self.backup_config.backup_amount, balance)
            backup_funds += backup_amount
            balance -= backup_amount
            backup_created = True
            logger.info(f"💰 Backup created: Balance hit ${self.backup_config.backup_activation_threshold:.0f}! Took ${backup_amount:.2f} → Balance ${balance:.2f}, Backup ${backup_funds:.2f}")
        
        return balance, backup_funds, backup_created
    
    def _track_milestones(self, risk_amount: float, balance: float, high_risk_count: int, 
                         high_risk_checkpoint: Optional[float], checkpoint_match_flag: bool, 
                         balance_4000_hit: bool) -> None:
        """Track various milestones during trading"""
        # Track high risk trades
        if risk_amount >= self.milestone_config.high_risk_threshold:
            high_risk_count += 1
            if high_risk_count == self.milestone_config.checkpoint_trades:
                high_risk_checkpoint = balance
        
        # Track balance milestones
        if balance >= self.leverage_config.upgrade_threshold and not balance_4000_hit:
            balance_4000_hit = True

class ExcelReporter:
    """Handle Excel report generation with formatting"""
    
    def __init__(self, excel_path: str = "simulation_report_upgraded.xlsx"):
        self.excel_path = excel_path
    
    def create_formats(self, workbook) -> Dict:
        """Create Excel formatting styles"""
        return {
            'blue': workbook.add_format({
                'bg_color': '#4F81BD', 
                'font_color': 'white', 
                'bold': True
            }),
            'green': workbook.add_format({
                'bg_color': '#00FF00', 
                'font_color': 'black', 
                'bold': True
            })
        }
    
    def apply_formatting(self, worksheet, df: pd.DataFrame, formats: Dict) -> None:
        """Apply conditional formatting to worksheet"""
        high_risk_count_excel = 0
        checkpoint_balance_excel = None
        checkpoint_matched = False
        balance_4000_matched = False
        final_milestone_matched = False
        
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
            
            # Apply formatting with priority
            if balance >= 500000 and not final_milestone_matched:
                worksheet.set_row(idx + 1, None, formats['green'])
                final_milestone_matched = True
            elif checkpoint_balance_excel and not checkpoint_matched and abs(balance - checkpoint_balance_excel) < 1e-6:
                worksheet.set_row(idx + 1, None, formats['green'])
                checkpoint_matched = True
            elif balance >= 4000 and not balance_4000_matched:
                worksheet.set_row(idx + 1, None, formats['green'])
                balance_4000_matched = True
            elif date_str.startswith('01/'):  # New month
                worksheet.set_row(idx + 1, None, formats['blue'])
    
    def generate_report(self, excel_data: Dict, summary_records: List[Dict]) -> None:
        """Generate the complete Excel report"""
        # Remove existing file
        if os.path.exists(self.excel_path):
            os.remove(self.excel_path)
        
        with pd.ExcelWriter(self.excel_path, engine="xlsxwriter") as writer:
            workbook = writer.book
            formats = self.create_formats(workbook)
            
            # Write all sheets
            for sheet_name, df in excel_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Apply formatting to simulation sheets
                if sheet_name != "Summary":
                    worksheet = writer.sheets[sheet_name]
                    self.apply_formatting(worksheet, df, formats)
        
        logger.info(f"✅ Excel report saved to: {self.excel_path}")

def main():
    """Main execution function"""
    logger.info("Starting Crypto Trading Simulation - Upgraded Version")
    
    # Initialize configurations
    trading_config = TradingConfig()
    leverage_config = LeverageConfig()
    milestone_config = MilestoneConfig()
    backup_config = BackupConfig()
    
    # Create simulator and reporter
    simulator = TradingSimulator(trading_config, leverage_config, milestone_config, backup_config)
    reporter = ExcelReporter()
    
    # Run simulations
    summary_records = []
    excel_data = {}
    
    for sim in range(1, trading_config.simulations + 1):
        df_log, milestone_dates, final_balance, first_trade_date, last_trade_date = simulator.simulate_trading_session(sim)
        
        # Calculate total time from actual trade dates
        if first_trade_date and last_trade_date:
            total_duration = last_trade_date - first_trade_date
            total_days = total_duration.days
            years_calc = total_days // 365
            months_calc = (total_days % 365) // 30
            days_calc = total_days % 30
        else:
            years_calc = months_calc = days_calc = 0
        
        excel_data[f"Sim {sim}"] = df_log
        record = {
            "Simulation": sim,
            "Final Balance": round(final_balance, 2),
            "First Trade": first_trade_date.strftime("%d/%m/%Y") if first_trade_date else "N/A",
            "Last Trade": last_trade_date.strftime("%d/%m/%Y") if last_trade_date else "N/A",
            "Total Days": total_days if first_trade_date and last_trade_date else 0,
            "Total Time": f"{years_calc}y {months_calc}m {days_calc}d"
        }
        summary_records.append(record)
    
    # Create summary and generate report
    df_summary = pd.DataFrame(summary_records)
    excel_data["Summary"] = df_summary
    
    reporter.generate_report(excel_data, summary_records)
    
    # Print summary statistics
    print("\n" + "="*60)
    print("SIMULATION SUMMARY")
    print("="*60)
    for record in summary_records:
        print(f"Simulation {record['Simulation']}: ${record['Final Balance']:,.2f} ({record['Total Time']})")
    print("="*60)

if __name__ == "__main__":
    main() 