"""
Run Backtest
============
הרצת בקטסט מלא על האסטרטגיות

בודק את כל 3 האסטרטגיות על נתונים היסטוריים
"""

import sys
import yaml
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from backtesting import BacktestEngine, PerformanceAnalyzer
from strategies import (
    EMACrossStrategy, 
    VWAPStrategy, 
    VolumeBreakoutStrategy, 
    MeanReversionStrategy,
    ORBStrategy,
    MomentumStrategy,
    BollingerBandsStrategy
)

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️  yfinance not installed. Using synthetic data.")


def download_real_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    הורדת נתונים אמיתיים מ-yfinance
    
    Args:
        symbol: סימול המניה
        start_date: תאריך התחלה (YYYY-MM-DD)
        end_date: תאריך סיום (YYYY-MM-DD)
        
    Returns:
        DataFrame עם OHLCV
    """
    if not YFINANCE_AVAILABLE:
        raise ImportError("yfinance is required for real data. Install: pip install yfinance")
    
    print(f"  Downloading {symbol} from {start_date} to {end_date}...")
    
    # הורדה מ-yfinance
    data = yf.download(symbol, start=start_date, end=end_date, interval='1d', progress=False)
    
    if data.empty:
        raise ValueError(f"No data downloaded for {symbol}")
    
    # המרת שמות עמודות לאותיות קטנות
    data.columns = [col.lower() for col in data.columns]
    
    # וידוא שיש את כל העמודות הנדרשות
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    for col in required_cols:
        if col not in data.columns:
            raise ValueError(f"Missing column: {col}")
    
    print(f"    ✓ Downloaded {len(data)} bars")
    
    return data


def generate_realistic_data(symbol: str, days: int = 60) -> pd.DataFrame:
    """
    יצירת נתונים מציאותיים למבחן
    
    Args:
        symbol: סימול המניה
        days: מספר ימים
        
    Returns:
        DataFrame עם OHLCV
    """
    # Number of 30-min bars (13 per day)
    bars_per_day = 13
    num_bars = days * bars_per_day
    
    # Base price based on symbol
    base_prices = {'AAPL': 150, 'GOOGL': 140, 'MSFT': 300}
    base_price = base_prices.get(symbol, 100)
    
    # Generate timestamps
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    timestamps = pd.date_range(start=start_time, end=end_time, periods=num_bars)
    
    # Generate price with realistic trend and noise
    trend = np.linspace(0, base_price * 0.15, num_bars)  # 15% trend
    
    # Add cycles (market cycles)
    cycle = np.sin(np.linspace(0, 4 * np.pi, num_bars)) * (base_price * 0.05)
    
    # Add noise
    noise = np.random.randn(num_bars) * (base_price * 0.02)
    
    # Combine
    close_prices = base_price + trend + cycle + noise
    
    # Ensure prices don't go negative
    close_prices = np.maximum(close_prices, base_price * 0.5)
    
    # Generate OHLC
    high_prices = close_prices + np.abs(np.random.randn(num_bars) * base_price * 0.01)
    low_prices = close_prices - np.abs(np.random.randn(num_bars) * base_price * 0.01)
    open_prices = close_prices + np.random.randn(num_bars) * base_price * 0.005
    
    # Volume with realistic patterns
    base_volume = 1_000_000
    volume_trend = np.linspace(base_volume, base_volume * 1.2, num_bars)
    volume_noise = np.random.rand(num_bars) * base_volume * 0.5
    volume = volume_trend + volume_noise
    
    # Add volume spikes randomly
    spike_indices = np.random.choice(num_bars, size=int(num_bars * 0.1), replace=False)
    volume[spike_indices] *= np.random.uniform(2, 4, size=len(spike_indices))
    
    df = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volume.astype(int)
    }, index=timestamps)
    
    return df


def print_header(text: str):
    """הדפסת כותרת"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def main():
    """הרצת בקטסט"""
    print_header("BACKTESTING SYSTEM")
    
    # Load config
    print("\nLoading configuration...")
    config_dir = Path(__file__).parent / 'config'
    
    with open(config_dir / 'risk_management.yaml', 'r', encoding='utf-8') as f:
        risk_config = yaml.safe_load(f)
    
    with open(config_dir / 'trading_config.yaml', 'r', encoding='utf-8') as f:
        trading_config = yaml.safe_load(f)
    
    # Merge configs
    config = {**risk_config, **trading_config}
    
    # Download REAL data from yfinance
    print("\n📥 Downloading REAL market data from yfinance...")
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    data = {}
    
    # Calculate dates (last 3 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print(f"  Period: {start_str} to {end_str}")
    
    try:
        for symbol in symbols:
            df = download_real_data(symbol, start_str, end_str)
            data[symbol] = df
            print(f"  ✅ {symbol}: {len(df)} bars, "
                  f"${df['close'].min():.2f} - ${df['close'].max():.2f}, "
                  f"Avg Volume: {df['volume'].mean():,.0f}")
    except Exception as e:
        print(f"\n⚠️  Failed to download real data: {e}")
        print("  Falling back to synthetic data...")
        for symbol in symbols:
            df = generate_realistic_data(symbol, days=90)
            data[symbol] = df
            print(f"  {symbol}: {len(df)} bars (synthetic)")
    
    # Initialize strategies
    print("\nInitializing strategies...")
    strategies = [
        EMACrossStrategy(trading_config['strategies']['ema_cross']),
        VWAPStrategy(trading_config['strategies']['vwap']),
        VolumeBreakoutStrategy(trading_config['strategies']['volume_breakout']),
        MeanReversionStrategy(trading_config['strategies']['Mean_Reversion']),
        ORBStrategy(trading_config['strategies']['ORB']),
        MomentumStrategy(trading_config['strategies']['Momentum']),
        BollingerBandsStrategy(trading_config['strategies']['Bollinger_Bands'])
    ]
    
    for strategy in strategies:
        print(f"  - {strategy.name}")
    
    # Run backtest for each strategy
    print_header("RUNNING BACKTESTS")
    
    all_results = {}
    
    for strategy in strategies:
        print(f"\n{'─' * 80}")
        print(f"Testing: {strategy.name}")
        print(f"{'─' * 80}")
        
        # Create backtest engine
        engine = BacktestEngine(config)
        
        # Run backtest
        try:
            results = engine.run(
                strategies=[strategy],
                data=data
            )
            
            # Print basic results
            engine.print_results()
            
            # Analyze performance
            analyzer = PerformanceAnalyzer(risk_free_rate=0.02)
            metrics = analyzer.analyze(
                equity_curve=results['equity_curve'],
                trades=results['trades'],
                initial_capital=config['account']['initial_capital']
            )
            
            # Print detailed metrics
            analyzer.print_metrics(metrics)
            
            # Save results
            all_results[strategy.name] = {
                'results': results,
                'metrics': metrics
            }
            
            # Show sample trades
            if results['trades']:
                print(f"\n📋 Sample Trades (first 5):")
                for i, trade in enumerate(results['trades'][:5], 1):
                    pnl_sign = "+" if trade.pnl > 0 else ""
                    print(f"  {i}. {trade.symbol:6} | "
                          f"Entry: ${trade.entry_price:>7.2f} | "
                          f"Exit: ${trade.exit_price:>7.2f} | "
                          f"PnL: {pnl_sign}${trade.pnl:>7.2f} ({pnl_sign}{trade.pnl_percent:>6.2f}%) | "
                          f"{trade.exit_reason}")
            
        except Exception as e:
            print(f"Error running backtest: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Compare strategies
    if len(all_results) > 1:
        print_header("STRATEGY COMPARISON")
        
        analyzer = PerformanceAnalyzer()
        comparison = analyzer.compare_strategies({
            name: result['metrics']
            for name, result in all_results.items()
        })
        
        print("\n" + comparison.to_string(index=False))
    
    print_header("BACKTEST COMPLETE")
    
    # Summary
    print("\nSummary:")
    for name, result in all_results.items():
        metrics = result['metrics']
        print(f"\n{name}:")
        print(f"  Return: {metrics.total_return:>8.2f}%")
        print(f"  Sharpe: {metrics.sharpe_ratio:>8.2f}")
        print(f"  Max DD: {metrics.max_drawdown:>8.2f}%")
        print(f"  Trades: {metrics.total_trades:>8}")
        print(f"  Win %:  {metrics.win_rate:>8.2f}%")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
