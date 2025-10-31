"""
Interactive Trading System Explorer
====================================

כלי אינטראקטיבי לחקר המערכת - תבחר מניה ותראה ניתוחים!
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from execution.broker_interface import IBBroker
from utils.data_processor import DataProcessor
from indicators.custom_indicators import TechnicalIndicators, SignalGenerator, add_all_indicators
from indicators.volume_analysis import VolumeAnalysis, VolumeBreakoutDetector, analyze_volume_characteristics
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 150)
pd.set_option('display.precision', 2)


def print_header(text):
    """Print a nice header."""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)


def print_section(text):
    """Print a section divider."""
    print("\n" + "-"*80)
    print(f"  {text}")
    print("-"*80)


def analyze_stock(broker, symbol, days=5):
    """Analyze a stock with all indicators."""
    
    print_header(f"📊 ניתוח מלא עבור {symbol}")
    
    # Get data
    print(f"\n🔄 מושך {days} ימים של נתונים...")
    bars = broker.get_historical_data(symbol, f"{days} D", "30 mins")
    
    if not bars:
        print(f"❌ לא הצלחתי למשוך נתונים עבור {symbol}")
        return None
    
    print(f"✅ קיבלתי {len(bars)} נרות")
    
    # Convert to DataFrame
    df = DataProcessor.bars_to_dataframe(bars)
    df = DataProcessor.validate_ohlcv(df)
    
    # Add all indicators
    print("🔧 מחשב אינדיקטורים...")
    df = add_all_indicators(df)
    
    # Add volume analysis
    df['volume_sma_20'] = VolumeAnalysis.volume_sma(df['volume'], 20)
    df['relative_volume'] = VolumeAnalysis.relative_volume(df['volume'], 20)
    df['obv'] = VolumeAnalysis.obv(df)
    df['cmf'] = VolumeAnalysis.chaikin_money_flow(df, 20)
    
    # Generate signals
    df['ema_signal'] = SignalGenerator.ema_cross_signal(df, 12, 26)
    df['rsi_signal'] = SignalGenerator.rsi_signal(df, 14, 30, 70)
    df['bb_signal'] = SignalGenerator.bollinger_signal(df, 20, 2.0)
    
    return df


def show_current_status(df, symbol):
    """Show current status and signals."""
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    print_section(f"📈 מצב נוכחי - {symbol}")
    
    # Price info
    print(f"""
מחיר:
  נוכחי:        ${latest['close']:.2f}
  שינוי יומי:   ${latest['close'] - prev['close']:+.2f} ({((latest['close']/prev['close']-1)*100):+.2f}%)
  גבוה היום:    ${df['high'].iloc[-13:].max():.2f}
  נמוך היום:    ${df['low'].iloc[-13:].min():.2f}
""")
    
    # Moving Averages
    print_section("📊 ממוצעים נעים")
    print(f"""
  EMA(12):      ${latest['ema_12']:.2f}  {'🟢' if latest['close'] > latest['ema_12'] else '🔴'}
  EMA(26):      ${latest['ema_26']:.2f}  {'🟢' if latest['close'] > latest['ema_26'] else '🔴'}
  EMA(50):      ${latest['ema_50']:.2f}  {'🟢' if latest['close'] > latest['ema_50'] else '🔴'}
  
  Trend:        {'📈 Bullish' if latest['ema_12'] > latest['ema_26'] > latest['ema_50'] else 
                 '📉 Bearish' if latest['ema_12'] < latest['ema_26'] < latest['ema_50'] else 
                 '↔️  Mixed'}
""")
    
    # VWAP
    print_section("💰 VWAP Analysis")
    vwap_diff = ((latest['close'] - latest['vwap']) / latest['vwap']) * 100
    print(f"""
  VWAP:         ${latest['vwap']:.2f}
  מחיר:         ${latest['close']:.2f}
  הפרש:         {vwap_diff:+.2f}%  {'🟢 Above' if vwap_diff > 0 else '🔴 Below'}
  
  פירוש:       {'מחיר חזק - מעל ממוצע נפח משוקלל' if vwap_diff > 0 else 'מחיר חלש - מתחת ממוצע נפח משוקלל'}
""")
    
    # RSI
    print_section("⚡ מומנטום (RSI)")
    rsi = latest['rsi']
    rsi_status = '🔴 Overbought' if rsi > 70 else '🟢 Oversold' if rsi < 30 else '⚪ Neutral'
    print(f"""
  RSI(14):      {rsi:.1f}  {rsi_status}
  
  {'⚠️  אזהרה: מצב overbought - שקול מכירה' if rsi > 70 else
   '✅ הזדמנות: מצב oversold - שקול קנייה' if rsi < 30 else
   'מומנטום נייטרלי'}
""")
    
    # Bollinger Bands
    print_section("📏 Bollinger Bands")
    bb_position = ((latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])) * 100
    print(f"""
  Upper:        ${latest['bb_upper']:.2f}
  Middle:       ${latest['bb_middle']:.2f}
  Lower:        ${latest['bb_lower']:.2f}
  Current:      ${latest['close']:.2f}
  
  מיקום:        {bb_position:.0f}% מהטווח  {'🔴 Near Upper' if bb_position > 80 else 
                                           '🟢 Near Lower' if bb_position < 20 else 
                                           '⚪ Middle'}
""")
    
    # Volume
    print_section("📊 ניתוח נפח")
    rel_vol = latest['relative_volume']
    vol_status = '🔊 Very High' if rel_vol > 2 else '🔉 High' if rel_vol > 1.5 else '🔇 Normal' if rel_vol > 0.8 else '📵 Low'
    print(f"""
  נפח נוכחי:    {latest['volume']:,.0f}
  נפח ממוצע:    {latest['volume_sma_20']:,.0f}
  יחסי:         {rel_vol:.2f}x  {vol_status}
  
  CMF:          {latest['cmf']:.3f}  {'🟢 Accumulation' if latest['cmf'] > 0 else '🔴 Distribution'}
  OBV Trend:    {'📈 Rising' if latest['obv'] > df['obv'].iloc[-5] else '📉 Falling'}
""")
    
    # Volatility
    print_section("🌊 תנודתיות")
    atr_pct = (latest['atr'] / latest['close']) * 100
    print(f"""
  ATR(14):      ${latest['atr']:.2f}
  ATR%:         {atr_pct:.2f}%
  
  תנודתיות:    {'🔴 High' if atr_pct > 3 else '🟡 Medium' if atr_pct > 1.5 else '🟢 Low'}
""")


def show_signals(df, symbol):
    """Show trading signals."""
    
    print_section(f"🎯 סיגנלי מסחר - {symbol}")
    
    latest = df.iloc[-1]
    recent_signals = df[['ema_signal', 'rsi_signal', 'bb_signal']].iloc[-5:]
    
    # EMA Cross Signal
    ema_signal = latest['ema_signal']
    if ema_signal == 1:
        print("\n  🟢 EMA CROSS BUY SIGNAL!")
        print("     EMA(12) חצה מעל EMA(26) - סיגנל bullish")
    elif ema_signal == -1:
        print("\n  🔴 EMA CROSS SELL SIGNAL!")
        print("     EMA(12) חצה מתחת EMA(26) - סיגנל bearish")
    else:
        trend = "Bullish 📈" if latest['ema_12'] > latest['ema_26'] else "Bearish 📉"
        print(f"\n  ⚪ EMA: No new signal - Current trend: {trend}")
    
    # RSI Signal
    rsi_signal = latest['rsi_signal']
    if rsi_signal == 1:
        print("\n  🟢 RSI BUY SIGNAL!")
        print(f"     RSI חצה מעל 30 - יציאה ממצב oversold")
    elif rsi_signal == -1:
        print("\n  🔴 RSI SELL SIGNAL!")
        print(f"     RSI חצה מתחת 70 - יציאה ממצב overbought")
    else:
        print(f"\n  ⚪ RSI: No signal - Current: {latest['rsi']:.1f}")
    
    # Bollinger Bands Signal
    bb_signal = latest['bb_signal']
    if bb_signal == 1:
        print("\n  🟢 BOLLINGER BANDS BUY SIGNAL!")
        print("     מחיר חזר מעל הפס התחתון - פוטנציאל לעלייה")
    elif bb_signal == -1:
        print("\n  🔴 BOLLINGER BANDS SELL SIGNAL!")
        print("     מחיר חזר מתחת הפס העליון - פוטנציאל לירידה")
    
    # Volume Spike
    if latest['relative_volume'] > 2:
        print("\n  🔊 VOLUME SPIKE ALERT!")
        print(f"     נפח חריג: {latest['relative_volume']:.1f}x מהממוצע")
        print("     אפשר לסמן מהלך משמעותי")
    
    # Consensus
    signals = [ema_signal, rsi_signal, bb_signal]
    bullish = signals.count(1)
    bearish = signals.count(-1)
    
    print_section("📊 סיכום סיגנלים")
    if bullish >= 2:
        print("\n  ✅ CONSENSUS: BULLISH")
        print(f"     {bullish} אינדיקטורים מראים buy signal")
    elif bearish >= 2:
        print("\n  ⚠️  CONSENSUS: BEARISH")
        print(f"     {bearish} אינדיקטורים מראים sell signal")
    else:
        print("\n  ⚪ CONSENSUS: MIXED/NEUTRAL")
        print("     אין הסכמה ברורה בין האינדיקטורים")


def show_statistics(df, symbol):
    """Show statistical analysis."""
    
    print_section(f"📈 סטטיסטיקות - {symbol}")
    
    # Price stats
    price_change = ((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100
    high = df['high'].max()
    low = df['low'].min()
    avg_volume = df['volume'].mean()
    
    print(f"""
תקופה:        {df.index[0].strftime('%Y-%m-%d')} - {df.index[-1].strftime('%Y-%m-%d')}
נרות:         {len(df)}

מחיר:
  התחלה:      ${df['close'].iloc[0]:.2f}
  סיום:        ${df['close'].iloc[-1]:.2f}
  שינוי:       {price_change:+.2f}%
  
טווח:
  גבוה:        ${high:.2f}
  נמוך:        ${low:.2f}
  טווח:        ${high - low:.2f} ({((high-low)/low)*100:.2f}%)

נפח:
  ממוצע:      {avg_volume:,.0f}
  מקסימום:    {df['volume'].max():,.0f}
  מינימום:    {df['volume'].min():,.0f}

תנודתיות:
  סטיית תקן:  ${df['close'].std():.2f}
  ATR ממוצע:  ${df['atr'].mean():.2f}
""")


def show_recent_bars(df, symbol, n=10):
    """Show recent price bars."""
    
    print_section(f"📊 {n} נרות אחרונים - {symbol}")
    
    recent = df[['open', 'high', 'low', 'close', 'volume']].tail(n)
    print("\n", recent.to_string())


def interactive_explorer():
    """Main interactive explorer."""
    
    print("\n" + "="*80)
    print("  🎮 TRADING SYSTEM EXPLORER")
    print("  חקור מניות עם כל האינדיקטורים!")
    print("="*80)
    
    # Connect
    print("\n📡 מתחבר ל-Interactive Brokers...")
    broker = IBBroker(port=7497)
    
    if not broker.connect():
        print("❌ לא הצלחתי להתחבר ל-IB. ודא ש-TWS פועל!")
        return
    
    print("✅ מחובר!\n")
    
    # Popular stocks
    popular_stocks = {
        '1': ('AAPL', 'Apple'),
        '2': ('MSFT', 'Microsoft'),
        '3': ('GOOGL', 'Google'),
        '4': ('AMZN', 'Amazon'),
        '5': ('TSLA', 'Tesla'),
        '6': ('NVDA', 'NVIDIA'),
        '7': ('META', 'Meta'),
        '8': ('NFLX', 'Netflix'),
    }
    
    while True:
        print("\n" + "="*80)
        print("  בחר מניה לניתוח:")
        print("="*80)
        
        for key, (symbol, name) in popular_stocks.items():
            print(f"  {key}. {symbol:6s} - {name}")
        
        print("  9. מניה אחרת (הקלד סימול)")
        print("  0. יציאה")
        
        choice = input("\nבחירה: ").strip()
        
        if choice == '0':
            print("\n👋 להתראות!")
            break
        
        if choice in popular_stocks:
            symbol, name = popular_stocks[choice]
        elif choice == '9':
            symbol = input("הקלד סימול (לדוגמה: AAPL): ").strip().upper()
            name = symbol
        else:
            print("❌ בחירה לא תקינה")
            continue
        
        # Analyze
        df = analyze_stock(broker, symbol, days=5)
        
        if df is None:
            continue
        
        # Show analysis menu
        while True:
            print("\n" + "="*80)
            print(f"  מה תרצה לראות עבור {symbol}?")
            print("="*80)
            print("  1. מצב נוכחי ואינדיקטורים")
            print("  2. סיגנלי מסחר")
            print("  3. סטטיסטיקות")
            print("  4. נרות אחרונים")
            print("  5. הכל!")
            print("  0. חזרה לבחירת מניה")
            
            sub_choice = input("\nבחירה: ").strip()
            
            if sub_choice == '0':
                break
            elif sub_choice == '1':
                show_current_status(df, symbol)
            elif sub_choice == '2':
                show_signals(df, symbol)
            elif sub_choice == '3':
                show_statistics(df, symbol)
            elif sub_choice == '4':
                show_recent_bars(df, symbol, 10)
            elif sub_choice == '5':
                show_current_status(df, symbol)
                show_signals(df, symbol)
                show_statistics(df, symbol)
                show_recent_bars(df, symbol, 5)
            else:
                print("❌ בחירה לא תקינה")
            
            input("\nלחץ Enter להמשך...")
    
    # Disconnect
    broker.disconnect()
    print("\n✅ התנתקתי מ-IB")
    print("\n" + "="*80)
    print("  תודה שהשתמשת ב-Trading System Explorer!")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        interactive_explorer()
    except KeyboardInterrupt:
        print("\n\n⚠️  יציאה...")
    except Exception as e:
        print(f"\n\n❌ שגיאה: {e}")
        import traceback
        traceback.print_exc()
