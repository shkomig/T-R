"""
Strategy Testing Script
======================
בדיקת כל האסטרטגיות עם נתונים היסטוריים

מריץ כל אסטרטגיה על מספר מניות ומציג:
- סיגנלים שהתקבלו
- אינדיקטורים
- Stop Loss / Take Profit
- גודל פוזיציה מומלץ
"""

import sys
import yaml
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from utils.data_processor import DataProcessor
from strategies import EMACrossStrategy, VWAPStrategy, VolumeBreakoutStrategy
from risk_management import PositionSizer, RiskCalculator

# Configuration
CONFIG_DIR = Path(__file__).parent / 'config'


def load_config(config_file: str) -> dict:
    """טעינת קובץ קונפיגורציה"""
    with open(CONFIG_DIR / config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def print_header(text: str):
    """הדפסת כותרת"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_subheader(text: str):
    """הדפסת כותרת משנה"""
    print(f"\n{'─' * 80}")
    print(f"  {text}")
    print(f"{'─' * 80}")


def test_strategy(strategy, symbol: str, data: pd.DataFrame, 
                 position_sizer: PositionSizer, account_balance: float = 100000):
    """
    בדיקת אסטרטגיה על מניה
    
    Args:
        strategy: האסטרטגיה לבדיקה
        symbol: סימול המניה
        data: נתונים היסטוריים
        position_sizer: מחשבון גודל פוזיציה
        account_balance: יתרת חשבון
    """
    print_subheader(f"{strategy.name} - {symbol}")
    
    try:
        # Analyze data
        print("📊 מנתח נתונים...")
        analyzed_data = strategy.analyze(data)
        
        # Generate signals
        print("🎯 מחפש סיגנלים...")
        signals = strategy.generate_signals(analyzed_data)
        
        if not signals:
            print("⚪ לא נמצאו סיגנלים במסגרת הזמן הזו")
            
            # Show current state anyway
            current = analyzed_data.iloc[-1]
            print(f"\nמצב נוכחי:")
            print(f"  מחיר: ${current['close']:.2f}")
            
            if 'ema_12' in current:
                print(f"  EMA(12): ${current['ema_12']:.2f}")
                print(f"  EMA(26): ${current['ema_26']:.2f}")
                print(f"  Trend: {current.get('trend', 'N/A')}")
            
            if 'vwap' in current:
                print(f"  VWAP: ${current['vwap']:.2f}")
                dist = current.get('vwap_distance_pct', 0)
                print(f"  Distance from VWAP: {dist:+.2f}%")
            
            if 'relative_volume' in current:
                print(f"  Relative Volume: {current['relative_volume']:.2f}x")
            
            return
        
        # Display signals
        print(f"\n✅ נמצאו {len(signals)} סיגנלים!\n")
        
        for i, signal in enumerate(signals, 1):
            print(f"סיגנל #{i}:")
            print(f"  🕒 זמן: {signal.timestamp}")
            print(f"  {'📈 BUY' if signal.signal_type.value == 'BUY' else '📉 SELL'}")
            print(f"  💰 מחיר: ${signal.price:.2f}")
            print(f"  💪 חוזק: {signal.strength.name} (confidence: {signal.confidence:.1%})")
            print(f"  📝 סיבה: {signal.reason}")
            
            # Risk management
            if signal.stop_loss:
                print(f"\n  🛑 Stop Loss: ${signal.stop_loss:.2f}")
                risk_amount = abs(signal.price - signal.stop_loss)
                risk_pct = (risk_amount / signal.price) * 100
                print(f"     Risk: ${risk_amount:.2f} ({risk_pct:.2f}% מהמחיר)")
            
            if signal.take_profit:
                print(f"  🎯 Take Profit: ${signal.take_profit:.2f}")
                reward = abs(signal.take_profit - signal.price)
                reward_pct = (reward / signal.price) * 100
                print(f"     Reward: ${reward:.2f} ({reward_pct:.2f}% מהמחיר)")
                
                if signal.stop_loss:
                    rr_ratio = reward / risk_amount
                    print(f"     Risk/Reward: 1:{rr_ratio:.2f}")
            
            # Position sizing
            if signal.stop_loss:
                shares = position_sizer.calculate_position_size(
                    account_balance=account_balance,
                    entry_price=signal.price,
                    stop_loss=signal.stop_loss
                )
                position_value = shares * signal.price
                risk_dollars = shares * abs(signal.price - signal.stop_loss)
                risk_percent = (risk_dollars / account_balance) * 100
                
                print(f"\n  📊 Position Sizing (Risk-Based):")
                print(f"     Shares: {shares}")
                print(f"     Position Value: ${position_value:,.2f}")
                print(f"     Total Risk: ${risk_dollars:.2f} ({risk_percent:.2f}% of account)")
            
            # Indicators
            if signal.indicators:
                print(f"\n  📈 Indicators:")
                for key, value in signal.indicators.items():
                    if isinstance(value, float):
                        print(f"     {key}: {value:.2f}")
                    else:
                        print(f"     {key}: {value}")
            
            print()
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()


def main():
    """הרצת בדיקות"""
    print_header("🧪 Strategy Testing - בדיקת אסטרטגיות")
    
    # Load configurations
    print("📁 טוען קונפיגורציות...")
    trading_config = load_config('trading_config.yaml')
    risk_config = load_config('risk_management.yaml')
    
    # Initialize broker
    print("🔌 מתחבר ל-Interactive Brokers...")
    broker_config = trading_config['broker']
    broker = IBBroker(broker_config)
    
    try:
        broker.connect()
        print("✅ מחובר!")
    except Exception as e:
        print(f"❌ שגיאת חיבור: {e}")
        print("⚠️  ממשיך בלי חיבור (לא יהיו נתונים חיים)")
        broker = None
    
    # Initialize components
    data_processor = DataProcessor()
    
    # Initialize strategies
    print("\n🎯 מאתחל אסטרטגיות...")
    strategies = {
        'EMA Cross': EMACrossStrategy(trading_config['strategies']['ema_cross']),
        'VWAP': VWAPStrategy(trading_config['strategies']['vwap']),
        'Volume Breakout': VolumeBreakoutStrategy(trading_config['strategies']['volume_breakout'])
    }
    
    # Initialize risk management
    position_sizer = PositionSizer(risk_config['position_sizing'])
    risk_calculator = RiskCalculator(risk_config)
    
    account_balance = risk_config['account']['initial_capital']
    print(f"💰 Account Balance: ${account_balance:,.2f}")
    
    # Test symbols
    test_symbols = ['AAPL', 'GOOGL', 'MSFT']
    
    print_header("🔍 מתחיל בדיקות")
    
    for symbol in test_symbols:
        print_header(f"📊 Testing {symbol}")
        
        if broker and broker.is_connected():
            # Get historical data
            print(f"📥 מושך נתונים עבור {symbol}...")
            try:
                bars = broker.get_historical_data(
                    symbol=symbol,
                    duration="5 D",
                    bar_size="30 mins"
                )
                
                if bars:
                    data = data_processor.bars_to_dataframe(bars)
                    print(f"✅ קיבלתי {len(data)} נרות")
                    print(f"   טווח: {data.index[0]} - {data.index[-1]}")
                    print(f"   מחיר אחרון: ${data['close'].iloc[-1]:.2f}")
                else:
                    print(f"❌ לא התקבלו נתונים עבור {symbol}")
                    continue
                    
            except Exception as e:
                print(f"❌ שגיאה בקבלת נתונים: {e}")
                continue
        else:
            print("⚠️  אין חיבור - דילוג על מניה זו")
            continue
        
        # Test each strategy
        for strategy_name, strategy in strategies.items():
            if not strategy.enabled:
                print(f"\n⚪ {strategy_name} - מושבת")
                continue
            
            test_strategy(
                strategy=strategy,
                symbol=symbol,
                data=data,
                position_sizer=position_sizer,
                account_balance=account_balance
            )
    
    # Cleanup
    if broker and broker.is_connected():
        print("\n🔌 מתנתק...")
        broker.disconnect()
    
    print_header("✅ בדיקות הושלמו!")


if __name__ == "__main__":
    main()
