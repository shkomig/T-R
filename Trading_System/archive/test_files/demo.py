"""
Quick Demo - Show What the System Can Do
=========================================

A quick demonstration of the trading system capabilities.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from utils.data_processor import DataProcessor
from indicators.custom_indicators import TechnicalIndicators, add_all_indicators
from indicators.volume_analysis import VolumeAnalysis, VolumeIndicatorSuite
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.precision', 2)


def demo():
    """Run a quick demo of the system."""
    
    print("\n" + "="*70)
    print("  TRADING SYSTEM DEMO - קדימה בואו נראה מה יש לנו!")
    print("="*70 + "\n")
    
    # Connect to IB
    print("📡 מתחבר ל-Interactive Brokers...")
    broker = IBBroker(port=7497)
    
    if not broker.connect():
        print("❌ לא הצלחתי להתחבר. ודא ש-TWS פועל!")
        return
    
    print("✅ מחובר בהצלחה!\n")
    
    # Get some data
    print("📊 מושך נתונים היסטוריים עבור AAPL...")
    symbol = "AAPL"
    bars = broker.get_historical_data(symbol, "5 D", "30 mins")
    
    if not bars:
        print("❌ לא הצלחתי למשוך נתונים")
        broker.disconnect()
        return
    
    print(f"✅ משכתי {len(bars)} נרות של 30 דקות\n")
    
    # Convert to DataFrame
    print("🔄 ממיר לפורמט DataFrame...")
    df = DataProcessor.bars_to_dataframe(bars)
    df = DataProcessor.validate_ohlcv(df)
    print(f"✅ יש לנו {len(df)} נרות נקיים\n")
    
    # Add indicators
    print("📈 מחשב אינדיקטורים טכניים...")
    df = add_all_indicators(df)
    print("✅ הוספתי: EMA, VWAP, RSI, Bollinger Bands, MACD, ATR\n")
    
    # Add volume analysis
    print("📊 מריץ ניתוח נפח מתקדם...")
    df = VolumeIndicatorSuite.add_all_volume_indicators(df)
    print("✅ הוספתי: OBV, A/D Line, CMF, Volume Breakout Signals\n")
    
    # Show latest data
    print("="*70)
    print("  הנתונים האחרונים (5 נרות אחרונים)")
    print("="*70)
    print(df[['open', 'high', 'low', 'close', 'volume']].tail())
    
    print("\n" + "="*70)
    print("  אינדיקטורים נוכחיים")
    print("="*70)
    
    latest = df.iloc[-1]
    print(f"""
    מחיר נוכחי:     ${latest['close']:.2f}
    
    ממוצעים נעים:
      EMA(12):      ${latest['ema_12']:.2f}
      EMA(26):      ${latest['ema_26']:.2f}
      EMA(50):      ${latest['ema_50']:.2f}
    
    VWAP:           ${latest['vwap']:.2f}
    
    מומנטום:
      RSI(14):      {latest['rsi']:.1f}
      
    Bollinger Bands:
      Upper:        ${latest['bb_upper']:.2f}
      Middle:       ${latest['bb_middle']:.2f}
      Lower:        ${latest['bb_lower']:.2f}
    
    תנודתיות:
      ATR(14):      ${latest['atr']:.2f}
    
    נפח:
      Relative Vol: {latest['relative_volume']:.2f}x
      CMF:          {latest['cmf']:.3f}
    """)
    
    # Check for signals
    print("="*70)
    print("  🎯 בדיקת סיגנלים")
    print("="*70)
    
    # EMA Cross
    if latest['ema_12'] > latest['ema_26']:
        print("  ✅ EMA Cross: Bullish (EMA12 מעל EMA26)")
    else:
        print("  ⚠️  EMA Cross: Bearish (EMA12 מתחת EMA26)")
    
    # RSI
    if latest['rsi'] < 30:
        print(f"  🟢 RSI: Oversold ({latest['rsi']:.1f}) - אפשרות לקנייה")
    elif latest['rsi'] > 70:
        print(f"  🔴 RSI: Overbought ({latest['rsi']:.1f}) - אפשרות למכירה")
    else:
        print(f"  ⚪ RSI: Neutral ({latest['rsi']:.1f})")
    
    # Price vs VWAP
    if latest['close'] > latest['vwap']:
        deviation = ((latest['close'] - latest['vwap']) / latest['vwap']) * 100
        print(f"  📈 Price above VWAP (+{deviation:.2f}%)")
    else:
        deviation = ((latest['vwap'] - latest['close']) / latest['vwap']) * 100
        print(f"  📉 Price below VWAP (-{deviation:.2f}%)")
    
    # Volume
    if latest['relative_volume'] > 1.5:
        print(f"  🔊 High Volume Alert! ({latest['relative_volume']:.1f}x normal)")
    elif latest['relative_volume'] > 1.0:
        print(f"  🔉 Normal to High Volume ({latest['relative_volume']:.1f}x)")
    else:
        print(f"  🔇 Low Volume ({latest['relative_volume']:.1f}x)")
    
    # Volume Breakout signals
    breakout_signals = df['volume_breakout'].iloc[-5:]
    if breakout_signals.any():
        if (breakout_signals == 1).any():
            print("  🚀 Volume Breakout: BULLISH signal detected!")
        if (breakout_signals == -1).any():
            print("  ⚠️  Volume Breakout: BEARISH signal detected!")
    
    print("\n" + "="*70)
    print("  📊 סטטיסטיקות כלליות (5 ימים)")
    print("="*70)
    
    print(f"""
    טווח מחירים:    ${df['low'].min():.2f} - ${df['high'].max():.2f}
    שינוי כולל:     {((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100):.2f}%
    נפח ממוצע:      {df['volume'].mean():,.0f}
    תנודתיות (std):  ${df['close'].std():.2f}
    """)
    
    # Disconnect
    broker.disconnect()
    
    print("="*70)
    print("  ✅ הדגמה הסתיימה בהצלחה!")
    print("="*70)
    print("""
    המערכת שלך:
    ✅ מתחברת ל-IB
    ✅ מושכת נתונים
    ✅ מחשבת 20+ אינדיקטורים
    ✅ מנתחת נפח
    ✅ מזהה סיגנלים
    
    🚀 מוכן לשלב הבא - פיתוח אסטרטגיות מסחר!
    """)


if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\nהופסק על ידי המשתמש")
    except Exception as e:
        print(f"\n\n❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()
