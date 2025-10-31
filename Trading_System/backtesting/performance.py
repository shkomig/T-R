"""
Performance Analyzer
===================
ניתוח ביצועים מתקדם לבקטסט

מחשב מדדי ביצועים סטנדרטיים:
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Maximum Drawdown
- Win Rate, Profit Factor
- Risk-adjusted returns
"""

from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """מדדי ביצועים מלאים"""
    # Returns
    total_return: float
    annualized_return: float
    daily_return_mean: float
    daily_return_std: float
    
    # Risk metrics
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    max_drawdown_duration: int  # days
    
    # Trade metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    profit_factor: float
    
    # Risk-reward
    avg_risk_reward: float
    expectancy: float
    
    # Time metrics
    avg_trade_duration: timedelta
    longest_trade: timedelta
    shortest_trade: timedelta
    
    # Other
    recovery_factor: float
    payoff_ratio: float


class PerformanceAnalyzer:
    """מחלקה לניתוח ביצועים"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        אתחול
        
        Args:
            risk_free_rate: ריבית חסרת סיכון (ברירת מחדל: 2%)
        """
        self.risk_free_rate = risk_free_rate
    
    def analyze(
        self,
        equity_curve: List[Tuple[datetime, float]],
        trades: List,
        initial_capital: float
    ) -> PerformanceMetrics:
        """
        ניתוח מלא של ביצועים
        
        Args:
            equity_curve: [(timestamp, equity), ...]
            trades: רשימת מסחרים
            initial_capital: הון התחלתי
            
        Returns:
            מדדי ביצועים
        """
        if not equity_curve or not trades:
            return self._empty_metrics()
        
        # Convert to DataFrame
        equity_df = pd.DataFrame(equity_curve, columns=['timestamp', 'equity'])
        equity_df.set_index('timestamp', inplace=True)
        
        # Calculate returns
        returns = equity_df['equity'].pct_change().dropna()
        
        # Total return
        total_return = ((equity_df['equity'].iloc[-1] - initial_capital) / initial_capital) * 100
        
        # Annualized return
        days = (equity_df.index[-1] - equity_df.index[0]).days
        years = days / 365.25
        annualized_return = ((equity_df['equity'].iloc[-1] / initial_capital) ** (1 / years) - 1) * 100 if years > 0 else 0
        
        # Daily statistics
        daily_return_mean = returns.mean() * 100
        daily_return_std = returns.std() * 100
        
        # Sharpe Ratio (annualized)
        excess_returns = returns - (self.risk_free_rate / 252)  # Daily risk-free rate
        sharpe_ratio = np.sqrt(252) * (excess_returns.mean() / returns.std()) if returns.std() > 0 else 0
        
        # Sortino Ratio (only downside deviation)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std()
        sortino_ratio = np.sqrt(252) * (excess_returns.mean() / downside_std) if downside_std > 0 else 0
        
        # Drawdown analysis
        max_dd, max_dd_duration = self._calculate_drawdown(equity_df['equity'])
        
        # Calmar Ratio
        calmar_ratio = (annualized_return / abs(max_dd)) if max_dd != 0 else 0
        
        # Trade statistics
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        total_trades = len(trades)
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        
        largest_win = max([t.pnl for t in winning_trades]) if winning_trades else 0
        largest_loss = min([t.pnl for t in losing_trades]) if losing_trades else 0
        
        # Profit factor
        gross_profit = sum(t.pnl for t in winning_trades)
        gross_loss = abs(sum(t.pnl for t in losing_trades))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Risk-reward metrics
        avg_risk_reward = (abs(avg_win) / abs(avg_loss)) if avg_loss != 0 else 0
        
        # Expectancy (average PnL per trade)
        expectancy = np.mean([t.pnl for t in trades]) if trades else 0
        
        # Trade duration
        durations = [t.duration for t in trades]
        avg_trade_duration = sum(durations, timedelta()) / len(durations) if durations else timedelta()
        longest_trade = max(durations) if durations else timedelta()
        shortest_trade = min(durations) if durations else timedelta()
        
        # Recovery factor (Net Profit / Max Drawdown)
        net_profit = equity_df['equity'].iloc[-1] - initial_capital
        recovery_factor = (net_profit / abs(max_dd * initial_capital / 100)) if max_dd != 0 else 0
        
        # Payoff ratio
        payoff_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        return PerformanceMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            daily_return_mean=daily_return_mean,
            daily_return_std=daily_return_std,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_dd,
            max_drawdown_duration=max_dd_duration,
            total_trades=total_trades,
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            profit_factor=profit_factor,
            avg_risk_reward=avg_risk_reward,
            expectancy=expectancy,
            avg_trade_duration=avg_trade_duration,
            longest_trade=longest_trade,
            shortest_trade=shortest_trade,
            recovery_factor=recovery_factor,
            payoff_ratio=payoff_ratio
        )
    
    def _calculate_drawdown(self, equity: pd.Series) -> Tuple[float, int]:
        """
        חישוב Max Drawdown ומשך הירידה
        
        Returns:
            (max_drawdown_percent, duration_in_days)
        """
        running_max = equity.expanding().max()
        drawdown = (equity - running_max) / running_max * 100
        
        max_dd = drawdown.min()
        
        # Find duration
        in_drawdown = drawdown < -0.01  # More than 0.01% drawdown
        drawdown_periods = []
        current_period = 0
        
        for is_dd in in_drawdown:
            if is_dd:
                current_period += 1
            else:
                if current_period > 0:
                    drawdown_periods.append(current_period)
                current_period = 0
        
        if current_period > 0:
            drawdown_periods.append(current_period)
        
        max_dd_duration = max(drawdown_periods) if drawdown_periods else 0
        
        return max_dd, max_dd_duration
    
    def _empty_metrics(self) -> PerformanceMetrics:
        """מדדים ריקים"""
        return PerformanceMetrics(
            total_return=0, annualized_return=0, daily_return_mean=0, daily_return_std=0,
            sharpe_ratio=0, sortino_ratio=0, calmar_ratio=0,
            max_drawdown=0, max_drawdown_duration=0,
            total_trades=0, winning_trades=0, losing_trades=0,
            win_rate=0, avg_win=0, avg_loss=0, largest_win=0, largest_loss=0,
            profit_factor=0, avg_risk_reward=0, expectancy=0,
            avg_trade_duration=timedelta(), longest_trade=timedelta(), shortest_trade=timedelta(),
            recovery_factor=0, payoff_ratio=0
        )
    
    def print_metrics(self, metrics: PerformanceMetrics):
        """הדפסת מדדים בפורמט יפה"""
        print("\n" + "=" * 80)
        print("  PERFORMANCE METRICS")
        print("=" * 80)
        
        print("\n📈 Returns:")
        print(f"  Total Return:        {metrics.total_return:>10.2f}%")
        print(f"  Annualized Return:   {metrics.annualized_return:>10.2f}%")
        print(f"  Daily Return (avg):  {metrics.daily_return_mean:>10.4f}%")
        print(f"  Daily Return (std):  {metrics.daily_return_std:>10.4f}%")
        
        print("\n⚖️  Risk Metrics:")
        print(f"  Sharpe Ratio:        {metrics.sharpe_ratio:>10.2f}")
        print(f"  Sortino Ratio:       {metrics.sortino_ratio:>10.2f}")
        print(f"  Calmar Ratio:        {metrics.calmar_ratio:>10.2f}")
        print(f"  Max Drawdown:        {metrics.max_drawdown:>10.2f}%")
        print(f"  Max DD Duration:     {metrics.max_drawdown_duration:>10} bars")
        
        print("\n📊 Trade Statistics:")
        print(f"  Total Trades:        {metrics.total_trades:>10}")
        print(f"  Winning Trades:      {metrics.winning_trades:>10} ({metrics.win_rate:.1f}%)")
        print(f"  Losing Trades:       {metrics.losing_trades:>10}")
        print(f"  Win Rate:            {metrics.win_rate:>10.2f}%")
        
        print("\n💰 Profit Analysis:")
        print(f"  Average Win:         ${metrics.avg_win:>10.2f}")
        print(f"  Average Loss:        ${metrics.avg_loss:>10.2f}")
        print(f"  Largest Win:         ${metrics.largest_win:>10.2f}")
        print(f"  Largest Loss:        ${metrics.largest_loss:>10.2f}")
        print(f"  Profit Factor:       {metrics.profit_factor:>10.2f}")
        print(f"  Payoff Ratio:        {metrics.payoff_ratio:>10.2f}")
        print(f"  Expectancy:          ${metrics.expectancy:>10.2f}")
        
        print("\n⏱️  Time Analysis:")
        print(f"  Avg Trade Duration:  {metrics.avg_trade_duration}")
        print(f"  Longest Trade:       {metrics.longest_trade}")
        print(f"  Shortest Trade:      {metrics.shortest_trade}")
        
        print("\n🎯 Other Metrics:")
        print(f"  Recovery Factor:     {metrics.recovery_factor:>10.2f}")
        print(f"  Risk/Reward Ratio:   {metrics.avg_risk_reward:>10.2f}")
        
        print("=" * 80)
    
    def compare_strategies(
        self,
        strategy_results: Dict[str, PerformanceMetrics]
    ) -> pd.DataFrame:
        """
        השוואת ביצועים בין אסטרטגיות
        
        Args:
            strategy_results: {strategy_name: metrics}
            
        Returns:
            DataFrame להשוואה
        """
        comparison_data = []
        
        for name, metrics in strategy_results.items():
            comparison_data.append({
                'Strategy': name,
                'Total Return %': metrics.total_return,
                'Sharpe': metrics.sharpe_ratio,
                'Max DD %': metrics.max_drawdown,
                'Win Rate %': metrics.win_rate,
                'Profit Factor': metrics.profit_factor,
                'Total Trades': metrics.total_trades,
                'Avg Win $': metrics.avg_win,
                'Avg Loss $': metrics.avg_loss
            })
        
        df = pd.DataFrame(comparison_data)
        df = df.sort_values('Total Return %', ascending=False)
        
        return df
