"""
Custom Technical Indicators Module
===================================

Implementation of custom technical indicators for trading strategies.

Author: Trading System
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Collection of technical indicators for market analysis.
    
    Indicators implemented:
    - EMA (Exponential Moving Average)
    - VWAP (Volume Weighted Average Price)
    - RSI (Relative Strength Index)
    - Bollinger Bands
    - ATR (Average True Range)
    - MACD (Moving Average Convergence Divergence)
    """
    
    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        """
        Calculate Exponential Moving Average.
        
        Args:
            series: Price series
            period: EMA period
        
        Returns:
            EMA series
        """
        try:
            ema_values = series.ewm(span=period, adjust=False).mean()
            logger.debug(f"Calculated EMA({period})")
            return ema_values
        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return pd.Series(index=series.index)
    
    @staticmethod
    def sma(series: pd.Series, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average.
        
        Args:
            series: Price series
            period: SMA period
        
        Returns:
            SMA series
        """
        try:
            sma_values = series.rolling(window=period).mean()
            logger.debug(f"Calculated SMA({period})")
            return sma_values
        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return pd.Series(index=series.index)
    
    @staticmethod
    def vwap(df: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume Weighted Average Price.
        
        Args:
            df: DataFrame with 'high', 'low', 'close', 'volume' columns
        
        Returns:
            VWAP series
        """
        try:
            # Typical price
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            
            # VWAP
            vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            
            logger.debug("Calculated VWAP")
            return vwap
        except Exception as e:
            logger.error(f"Error calculating VWAP: {e}")
            return pd.Series(index=df.index)
    
    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            series: Price series
            period: RSI period (default: 14)
        
        Returns:
            RSI series (0-100)
        """
        try:
            # Calculate price changes
            delta = series.diff()
            
            # Separate gains and losses
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            
            # Calculate average gains and losses
            avg_gains = gains.ewm(span=period, adjust=False).mean()
            avg_losses = losses.ewm(span=period, adjust=False).mean()
            
            # Calculate RS and RSI
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))
            
            logger.debug(f"Calculated RSI({period})")
            return rsi
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series(index=series.index)
    
    @staticmethod
    def bollinger_bands(
        series: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            series: Price series
            period: Moving average period (default: 20)
            std_dev: Standard deviations (default: 2.0)
        
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        try:
            # Middle band (SMA)
            middle_band = series.rolling(window=period).mean()
            
            # Standard deviation
            std = series.rolling(window=period).std()
            
            # Upper and lower bands
            upper_band = middle_band + (std_dev * std)
            lower_band = middle_band - (std_dev * std)
            
            logger.debug(f"Calculated Bollinger Bands({period}, {std_dev})")
            return upper_band, middle_band, lower_band
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return (pd.Series(index=series.index), 
                    pd.Series(index=series.index),
                    pd.Series(index=series.index))
    
    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range.
        
        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            period: ATR period (default: 14)
        
        Returns:
            ATR series
        """
        try:
            # True Range components
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            
            # True Range
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            
            # Average True Range
            atr = true_range.ewm(span=period, adjust=False).mean()
            
            logger.debug(f"Calculated ATR({period})")
            return atr
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return pd.Series(index=df.index)
    
    @staticmethod
    def macd(
        series: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            series: Price series
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line period (default: 9)
        
        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        try:
            # MACD line
            ema_fast = series.ewm(span=fast, adjust=False).mean()
            ema_slow = series.ewm(span=slow, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            
            # Signal line
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            
            # Histogram
            histogram = macd_line - signal_line
            
            logger.debug(f"Calculated MACD({fast}, {slow}, {signal})")
            return macd_line, signal_line, histogram
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return (pd.Series(index=series.index),
                    pd.Series(index=series.index),
                    pd.Series(index=series.index))
    
    @staticmethod
    def stochastic(
        df: pd.DataFrame,
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator.
        
        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            k_period: %K period (default: 14)
            d_period: %D period (default: 3)
        
        Returns:
            Tuple of (%K, %D)
        """
        try:
            # Lowest low and highest high
            low_min = df['low'].rolling(window=k_period).min()
            high_max = df['high'].rolling(window=k_period).max()
            
            # %K
            k_percent = 100 * (df['close'] - low_min) / (high_max - low_min)
            
            # %D (moving average of %K)
            d_percent = k_percent.rolling(window=d_period).mean()
            
            logger.debug(f"Calculated Stochastic({k_period}, {d_period})")
            return k_percent, d_percent
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return (pd.Series(index=df.index),
                    pd.Series(index=df.index))
    
    @staticmethod
    def adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average Directional Index.
        
        Args:
            df: DataFrame with 'high', 'low', 'close' columns
            period: ADX period (default: 14)
        
        Returns:
            ADX series
        """
        try:
            # True Range
            tr = TechnicalIndicators.atr(df, period=1)
            
            # Directional Movement
            high_diff = df['high'] - df['high'].shift()
            low_diff = df['low'].shift() - df['low']
            
            plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
            minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
            
            # Smoothed DM and TR
            plus_di = 100 * (plus_dm.ewm(span=period).mean() / tr.ewm(span=period).mean())
            minus_di = 100 * (minus_dm.ewm(span=period).mean() / tr.ewm(span=period).mean())
            
            # DX and ADX
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.ewm(span=period).mean()
            
            logger.debug(f"Calculated ADX({period})")
            return adx
        except Exception as e:
            logger.error(f"Error calculating ADX: {e}")
            return pd.Series(index=df.index)


class SignalGenerator:
    """Generate trading signals based on indicators."""
    
    @staticmethod
    def ema_cross_signal(
        df: pd.DataFrame,
        fast_period: int = 12,
        slow_period: int = 26
    ) -> pd.Series:
        """
        Generate EMA crossover signals.
        
        Args:
            df: DataFrame with 'close' column
            fast_period: Fast EMA period
            slow_period: Slow EMA period
        
        Returns:
            Signal series: 1=buy, -1=sell, 0=hold
        """
        try:
            ema_fast = TechnicalIndicators.ema(df['close'], fast_period)
            ema_slow = TechnicalIndicators.ema(df['close'], slow_period)
            
            # Crossover signals
            signals = pd.Series(0, index=df.index)
            
            # Buy signal: fast crosses above slow
            signals[(ema_fast > ema_slow) & (ema_fast.shift() <= ema_slow.shift())] = 1
            
            # Sell signal: fast crosses below slow
            signals[(ema_fast < ema_slow) & (ema_fast.shift() >= ema_slow.shift())] = -1
            
            logger.debug(f"Generated EMA cross signals ({fast_period}/{slow_period})")
            return signals
        except Exception as e:
            logger.error(f"Error generating EMA cross signals: {e}")
            return pd.Series(0, index=df.index)
    
    @staticmethod
    def rsi_signal(
        df: pd.DataFrame,
        period: int = 14,
        oversold: float = 30,
        overbought: float = 70
    ) -> pd.Series:
        """
        Generate RSI-based signals.
        
        Args:
            df: DataFrame with 'close' column
            period: RSI period
            oversold: Oversold threshold (default: 30)
            overbought: Overbought threshold (default: 70)
        
        Returns:
            Signal series: 1=buy, -1=sell, 0=hold
        """
        try:
            rsi = TechnicalIndicators.rsi(df['close'], period)
            
            signals = pd.Series(0, index=df.index)
            
            # Buy signal: RSI crosses above oversold
            signals[(rsi > oversold) & (rsi.shift() <= oversold)] = 1
            
            # Sell signal: RSI crosses below overbought
            signals[(rsi < overbought) & (rsi.shift() >= overbought)] = -1
            
            logger.debug(f"Generated RSI signals ({period})")
            return signals
        except Exception as e:
            logger.error(f"Error generating RSI signals: {e}")
            return pd.Series(0, index=df.index)
    
    @staticmethod
    def bollinger_signal(
        df: pd.DataFrame,
        period: int = 20,
        std_dev: float = 2.0
    ) -> pd.Series:
        """
        Generate Bollinger Bands signals.
        
        Args:
            df: DataFrame with 'close' column
            period: BB period
            std_dev: Standard deviations
        
        Returns:
            Signal series: 1=buy, -1=sell, 0=hold
        """
        try:
            upper, middle, lower = TechnicalIndicators.bollinger_bands(
                df['close'], period, std_dev
            )
            
            signals = pd.Series(0, index=df.index)
            
            # Buy signal: price crosses above lower band
            signals[(df['close'] > lower) & (df['close'].shift() <= lower.shift())] = 1
            
            # Sell signal: price crosses below upper band
            signals[(df['close'] < upper) & (df['close'].shift() >= upper.shift())] = -1
            
            logger.debug(f"Generated Bollinger Bands signals ({period}, {std_dev})")
            return signals
        except Exception as e:
            logger.error(f"Error generating Bollinger signals: {e}")
            return pd.Series(0, index=df.index)


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all technical indicators to DataFrame.
    
    Args:
        df: DataFrame with OHLCV data
    
    Returns:
        DataFrame with added indicator columns
    """
    try:
        df = df.copy()
        
        # EMAs
        df['ema_12'] = TechnicalIndicators.ema(df['close'], 12)
        df['ema_26'] = TechnicalIndicators.ema(df['close'], 26)
        df['ema_50'] = TechnicalIndicators.ema(df['close'], 50)
        
        # VWAP
        df['vwap'] = TechnicalIndicators.vwap(df)
        
        # RSI
        df['rsi'] = TechnicalIndicators.rsi(df['close'], 14)
        
        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = \
            TechnicalIndicators.bollinger_bands(df['close'], 20, 2.0)
        
        # ATR
        df['atr'] = TechnicalIndicators.atr(df, 14)
        
        # MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = \
            TechnicalIndicators.macd(df['close'], 12, 26, 9)
        
        logger.info("Added all technical indicators")
        return df
    except Exception as e:
        logger.error(f"Error adding all indicators: {e}")
        return df
