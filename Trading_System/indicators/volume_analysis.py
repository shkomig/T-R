"""
Volume Analysis Module
======================

Advanced volume analysis tools for detecting unusual trading activity
and volume-based trading signals.

Author: Trading System
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class VolumeAnalysis:
    """
    Volume-based technical analysis tools.
    
    Features:
    - Volume Profile
    - High-Volume Detection
    - Volume Breakout Signals
    - Volume-Weighted Indicators
    - Accumulation/Distribution
    """
    
    @staticmethod
    def volume_sma(volume: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate Simple Moving Average of volume.
        
        Args:
            volume: Volume series
            period: SMA period (default: 20)
        
        Returns:
            Volume SMA series
        """
        try:
            vol_sma = volume.rolling(window=period).mean()
            logger.debug(f"Calculated Volume SMA({period})")
            return vol_sma
        except Exception as e:
            logger.error(f"Error calculating volume SMA: {e}")
            return pd.Series(index=volume.index)
    
    @staticmethod
    def relative_volume(volume: pd.Series, period: int = 20) -> pd.Series:
        """
        Calculate relative volume (current volume / average volume).
        
        Args:
            volume: Volume series
            period: Period for average calculation
        
        Returns:
            Relative volume series (1.0 = average)
        """
        try:
            avg_volume = volume.rolling(window=period).mean()
            rel_volume = volume / avg_volume
            
            logger.debug(f"Calculated Relative Volume({period})")
            return rel_volume
        except Exception as e:
            logger.error(f"Error calculating relative volume: {e}")
            return pd.Series(1.0, index=volume.index)
    
    @staticmethod
    def detect_high_volume(
        volume: pd.Series,
        threshold: float = 1.5,
        period: int = 20
    ) -> pd.Series:
        """
        Detect bars with unusually high volume.
        
        Args:
            volume: Volume series
            threshold: Multiplier threshold (e.g., 1.5 = 150% of average)
            period: Period for average calculation
        
        Returns:
            Boolean series indicating high volume bars
        """
        try:
            rel_volume = VolumeAnalysis.relative_volume(volume, period)
            high_volume = rel_volume >= threshold
            
            count = high_volume.sum()
            logger.info(f"Detected {count} high-volume bars (threshold: {threshold}x)")
            return high_volume
        except Exception as e:
            logger.error(f"Error detecting high volume: {e}")
            return pd.Series(False, index=volume.index)
    
    @staticmethod
    def volume_profile(
        df: pd.DataFrame,
        price_bins: int = 20
    ) -> Dict[str, Any]:
        """
        Calculate Volume Profile (volume distribution by price level).
        
        Args:
            df: DataFrame with 'close' and 'volume' columns
            price_bins: Number of price bins
        
        Returns:
            Dictionary with volume profile data
        """
        try:
            # Create price bins
            price_min = df['close'].min()
            price_max = df['close'].max()
            bins = np.linspace(price_min, price_max, price_bins + 1)
            
            # Assign each bar to a price bin
            df_temp = df.copy()
            df_temp['price_bin'] = pd.cut(df_temp['close'], bins=bins)
            
            # Sum volume for each price level
            volume_by_price = df_temp.groupby('price_bin')['volume'].sum()
            
            # Find Point of Control (POC) - price with highest volume
            poc_bin = volume_by_price.idxmax()
            poc_price = poc_bin.mid
            
            # Value Area (70% of volume)
            total_volume = volume_by_price.sum()
            target_volume = total_volume * 0.70
            
            sorted_volumes = volume_by_price.sort_values(ascending=False)
            cumsum = 0
            value_area_bins = []
            
            for bin_label, vol in sorted_volumes.items():
                cumsum += vol
                value_area_bins.append(bin_label)
                if cumsum >= target_volume:
                    break
            
            value_area_high = max([b.right for b in value_area_bins])
            value_area_low = min([b.left for b in value_area_bins])
            
            profile = {
                'volume_by_price': volume_by_price,
                'poc': poc_price,
                'value_area_high': value_area_high,
                'value_area_low': value_area_low,
                'total_volume': total_volume
            }
            
            logger.info(f"Calculated Volume Profile - POC: ${poc_price:.2f}")
            return profile
            
        except Exception as e:
            logger.error(f"Error calculating volume profile: {e}")
            return {}
    
    @staticmethod
    def obv(df: pd.DataFrame) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV).
        
        Args:
            df: DataFrame with 'close' and 'volume' columns
        
        Returns:
            OBV series
        """
        try:
            # Price direction
            price_change = df['close'].diff()
            
            # Volume direction
            obv = pd.Series(0, index=df.index, dtype=float)
            obv[price_change > 0] = df['volume']
            obv[price_change < 0] = -df['volume']
            obv[price_change == 0] = 0
            
            # Cumulative sum
            obv = obv.cumsum()
            
            logger.debug("Calculated OBV")
            return obv
        except Exception as e:
            logger.error(f"Error calculating OBV: {e}")
            return pd.Series(index=df.index)
    
    @staticmethod
    def accumulation_distribution(df: pd.DataFrame) -> pd.Series:
        """
        Calculate Accumulation/Distribution Line.
        
        Args:
            df: DataFrame with OHLCV columns
        
        Returns:
            A/D Line series
        """
        try:
            # Money Flow Multiplier
            clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
            
            # Handle division by zero
            clv = clv.fillna(0)
            
            # Money Flow Volume
            mfv = clv * df['volume']
            
            # Accumulation/Distribution Line
            ad_line = mfv.cumsum()
            
            logger.debug("Calculated Accumulation/Distribution Line")
            return ad_line
        except Exception as e:
            logger.error(f"Error calculating A/D Line: {e}")
            return pd.Series(index=df.index)
    
    @staticmethod
    def chaikin_money_flow(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Chaikin Money Flow (CMF).
        
        Args:
            df: DataFrame with OHLCV columns
            period: CMF period (default: 20)
        
        Returns:
            CMF series
        """
        try:
            # Money Flow Multiplier
            clv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low'])
            clv = clv.fillna(0)
            
            # Money Flow Volume
            mfv = clv * df['volume']
            
            # CMF
            cmf = mfv.rolling(window=period).sum() / df['volume'].rolling(window=period).sum()
            
            logger.debug(f"Calculated Chaikin Money Flow({period})")
            return cmf
        except Exception as e:
            logger.error(f"Error calculating CMF: {e}")
            return pd.Series(index=df.index)
    
    @staticmethod
    def volume_rate_of_change(volume: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Volume Rate of Change.
        
        Args:
            volume: Volume series
            period: ROC period
        
        Returns:
            Volume ROC series (percentage)
        """
        try:
            vol_roc = ((volume - volume.shift(period)) / volume.shift(period)) * 100
            logger.debug(f"Calculated Volume ROC({period})")
            return vol_roc
        except Exception as e:
            logger.error(f"Error calculating Volume ROC: {e}")
            return pd.Series(index=volume.index)
    
    @staticmethod
    def price_volume_trend(df: pd.DataFrame) -> pd.Series:
        """
        Calculate Price Volume Trend (PVT).
        
        Args:
            df: DataFrame with 'close' and 'volume' columns
        
        Returns:
            PVT series
        """
        try:
            # Price change percentage
            price_change_pct = df['close'].pct_change()
            
            # PVT
            pvt = (price_change_pct * df['volume']).cumsum()
            
            logger.debug("Calculated Price Volume Trend")
            return pvt
        except Exception as e:
            logger.error(f"Error calculating PVT: {e}")
            return pd.Series(index=df.index)


class VolumeBreakoutDetector:
    """
    Detect volume breakouts for trading signals.
    """
    
    @staticmethod
    def detect_breakout(
        df: pd.DataFrame,
        volume_threshold: float = 1.5,
        price_threshold: float = 0.5,
        confirmation_bars: int = 3,
        lookback_period: int = 20
    ) -> pd.Series:
        """
        Detect volume breakout with price confirmation.
        
        Args:
            df: DataFrame with OHLCV columns
            volume_threshold: Volume multiplier (1.5 = 150% of average)
            price_threshold: Minimum price change % for confirmation
            confirmation_bars: Number of bars to confirm breakout
            lookback_period: Period for average calculation
        
        Returns:
            Signal series: 1=bullish breakout, -1=bearish breakout, 0=no signal
        """
        try:
            # High volume detection
            high_volume = VolumeAnalysis.detect_high_volume(
                df['volume'], volume_threshold, lookback_period
            )
            
            # Price movement
            price_change_pct = df['close'].pct_change() * 100
            
            # Initialize signals
            signals = pd.Series(0, index=df.index)
            
            # Bullish breakout: high volume + price increase
            bullish_condition = (
                high_volume &
                (price_change_pct >= price_threshold)
            )
            
            # Bearish breakout: high volume + price decrease
            bearish_condition = (
                high_volume &
                (price_change_pct <= -price_threshold)
            )
            
            # Apply confirmation (next N bars should continue the trend)
            for i in range(len(df)):
                if bullish_condition.iloc[i]:
                    # Check confirmation
                    if i + confirmation_bars < len(df):
                        future_bars = df.iloc[i:i+confirmation_bars]
                        if (future_bars['close'].iloc[-1] > future_bars['close'].iloc[0]):
                            signals.iloc[i] = 1
                
                elif bearish_condition.iloc[i]:
                    # Check confirmation
                    if i + confirmation_bars < len(df):
                        future_bars = df.iloc[i:i+confirmation_bars]
                        if (future_bars['close'].iloc[-1] < future_bars['close'].iloc[0]):
                            signals.iloc[i] = -1
            
            bullish_count = (signals == 1).sum()
            bearish_count = (signals == -1).sum()
            logger.info(f"Detected {bullish_count} bullish, {bearish_count} bearish volume breakouts")
            
            return signals
            
        except Exception as e:
            logger.error(f"Error detecting breakout: {e}")
            return pd.Series(0, index=df.index)
    
    @staticmethod
    def volume_spike_with_reversal(
        df: pd.DataFrame,
        volume_threshold: float = 2.0,
        reversal_threshold: float = 1.0,
        lookback_period: int = 20
    ) -> pd.Series:
        """
        Detect volume spikes that may indicate reversals.
        
        Args:
            df: DataFrame with OHLCV columns
            volume_threshold: Volume spike threshold
            reversal_threshold: Price reversal percentage
            lookback_period: Lookback period
        
        Returns:
            Signal series: 1=potential bullish reversal, -1=potential bearish reversal
        """
        try:
            # High volume spikes
            high_volume = VolumeAnalysis.detect_high_volume(
                df['volume'], volume_threshold, lookback_period
            )
            
            # Price direction
            price_change = df['close'].pct_change() * 100
            prev_trend = df['close'].rolling(window=5).mean().diff()
            
            signals = pd.Series(0, index=df.index)
            
            # Bullish reversal: volume spike during downtrend + price reversal up
            bullish_reversal = (
                high_volume &
                (prev_trend < 0) &
                (price_change > reversal_threshold)
            )
            
            # Bearish reversal: volume spike during uptrend + price reversal down
            bearish_reversal = (
                high_volume &
                (prev_trend > 0) &
                (price_change < -reversal_threshold)
            )
            
            signals[bullish_reversal] = 1
            signals[bearish_reversal] = -1
            
            logger.info(f"Detected {(signals != 0).sum()} potential reversal signals")
            return signals
            
        except Exception as e:
            logger.error(f"Error detecting reversal: {e}")
            return pd.Series(0, index=df.index)


class VolumeIndicatorSuite:
    """
    Complete suite of volume indicators for a DataFrame.
    """
    
    @staticmethod
    def add_all_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all volume indicators to DataFrame.
        
        Args:
            df: DataFrame with OHLCV columns
        
        Returns:
            DataFrame with added volume indicator columns
        """
        try:
            df = df.copy()
            
            # Basic volume metrics
            df['volume_sma_20'] = VolumeAnalysis.volume_sma(df['volume'], 20)
            df['relative_volume'] = VolumeAnalysis.relative_volume(df['volume'], 20)
            df['high_volume'] = VolumeAnalysis.detect_high_volume(df['volume'], 1.5, 20)
            
            # Volume indicators
            df['obv'] = VolumeAnalysis.obv(df)
            df['ad_line'] = VolumeAnalysis.accumulation_distribution(df)
            df['cmf'] = VolumeAnalysis.chaikin_money_flow(df, 20)
            df['volume_roc'] = VolumeAnalysis.volume_rate_of_change(df['volume'], 14)
            df['pvt'] = VolumeAnalysis.price_volume_trend(df)
            
            # Breakout signals
            df['volume_breakout'] = VolumeBreakoutDetector.detect_breakout(
                df, volume_threshold=1.5, confirmation_bars=3
            )
            df['volume_reversal'] = VolumeBreakoutDetector.volume_spike_with_reversal(
                df, volume_threshold=2.0
            )
            
            logger.info("Added all volume indicators to DataFrame")
            return df
            
        except Exception as e:
            logger.error(f"Error adding volume indicators: {e}")
            return df


def analyze_volume_characteristics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Comprehensive volume analysis summary.
    
    Args:
        df: DataFrame with volume data
    
    Returns:
        Dictionary with volume statistics and characteristics
    """
    try:
        analysis = {
            'average_volume': df['volume'].mean(),
            'median_volume': df['volume'].median(),
            'max_volume': df['volume'].max(),
            'min_volume': df['volume'].min(),
            'std_volume': df['volume'].std(),
            'volume_trend': 'increasing' if df['volume'].iloc[-20:].mean() > df['volume'].iloc[-40:-20].mean() else 'decreasing',
            'high_volume_days': VolumeAnalysis.detect_high_volume(df['volume'], 1.5, 20).sum(),
            'avg_relative_volume': VolumeAnalysis.relative_volume(df['volume'], 20).mean()
        }
        
        logger.info("Completed volume characteristics analysis")
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing volume characteristics: {e}")
        return {}


# Helper function for volume-based entry signals
def get_volume_entry_signals(
    df: pd.DataFrame,
    strategy: str = "breakout"
) -> pd.Series:
    """
    Get volume-based entry signals.
    
    Args:
        df: DataFrame with OHLCV columns
        strategy: "breakout" or "reversal"
    
    Returns:
        Signal series: 1=long, -1=short, 0=no signal
    """
    if strategy == "breakout":
        return VolumeBreakoutDetector.detect_breakout(df)
    elif strategy == "reversal":
        return VolumeBreakoutDetector.volume_spike_with_reversal(df)
    else:
        logger.warning(f"Unknown strategy: {strategy}")
        return pd.Series(0, index=df.index)
