"""
Data Processor Module
=====================

Handles market data processing, formatting, and validation.

Author: Trading System
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Process and clean market data from various sources.
    
    Features:
    - Convert IB bars to pandas DataFrame
    - Data validation and cleaning
    - OHLCV processing
    - Resampling to different timeframes
    """
    
    @staticmethod
    def bars_to_dataframe(bars: Any) -> pd.DataFrame:
        """
        Convert IB bars to pandas DataFrame.
        
        Args:
            bars: BarDataList from ib_insync
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if not bars:
                logger.warning("Empty bars list received")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'date': bar.date,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume,
                'average': bar.average,
                'barCount': bar.barCount
            } for bar in bars])
            
            # Set date as index
            df.set_index('date', inplace=True)
            
            # Ensure proper data types
            df = df.astype({
                'open': float,
                'high': float,
                'low': float,
                'close': float,
                'volume': int,
                'average': float
            })
            
            logger.info(f"Converted {len(df)} bars to DataFrame")
            return df
            
        except Exception as e:
            logger.error(f"Error converting bars to DataFrame: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and clean OHLCV data.
        
        Args:
            df: DataFrame with OHLCV columns
        
        Returns:
            Cleaned DataFrame
        """
        try:
            if df.empty:
                return df
            
            # Remove rows with missing values
            df_clean = df.dropna()
            
            # Validate OHLC relationships
            # High should be >= Open, Close, Low
            # Low should be <= Open, Close, High
            invalid_rows = (
                (df_clean['high'] < df_clean['low']) |
                (df_clean['high'] < df_clean['open']) |
                (df_clean['high'] < df_clean['close']) |
                (df_clean['low'] > df_clean['open']) |
                (df_clean['low'] > df_clean['close'])
            )
            
            if invalid_rows.any():
                logger.warning(f"Found {invalid_rows.sum()} invalid OHLC rows, removing...")
                df_clean = df_clean[~invalid_rows]
            
            # Remove negative values
            df_clean = df_clean[
                (df_clean['open'] > 0) &
                (df_clean['high'] > 0) &
                (df_clean['low'] > 0) &
                (df_clean['close'] > 0) &
                (df_clean['volume'] >= 0)
            ]
            
            # Remove duplicates
            df_clean = df_clean[~df_clean.index.duplicated(keep='first')]
            
            logger.info(f"Cleaned data: {len(df)} -> {len(df_clean)} rows")
            return df_clean
            
        except Exception as e:
            logger.error(f"Error validating OHLCV data: {e}")
            return df
    
    @staticmethod
    def resample_bars(
        df: pd.DataFrame,
        timeframe: str = "30min",
        method: str = "ohlc"
    ) -> pd.DataFrame:
        """
        Resample bars to different timeframe.
        
        Args:
            df: DataFrame with OHLCV data
            timeframe: Target timeframe (e.g., "5min", "15min", "1H", "1D")
            method: Resampling method ("ohlc" or "last")
        
        Returns:
            Resampled DataFrame
        """
        try:
            if df.empty:
                return df
            
            # OHLCV aggregation rules
            agg_dict = {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }
            
            # Resample
            df_resampled = df.resample(timeframe).agg(agg_dict)
            
            # Remove rows with NaN (no data in that period)
            df_resampled = df_resampled.dropna()
            
            logger.info(f"Resampled to {timeframe}: {len(df)} -> {len(df_resampled)} bars")
            return df_resampled
            
        except Exception as e:
            logger.error(f"Error resampling bars: {e}")
            return df
    
    @staticmethod
    def add_basic_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add basic derived features to DataFrame.
        
        Features added:
        - returns: Percentage returns
        - log_returns: Logarithmic returns
        - range: High - Low
        - body: Close - Open
        - upper_shadow: High - max(Open, Close)
        - lower_shadow: min(Open, Close) - Low
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with additional features
        """
        try:
            if df.empty:
                return df
            
            df = df.copy()
            
            # Returns
            df['returns'] = df['close'].pct_change()
            df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
            
            # Candle features
            df['range'] = df['high'] - df['low']
            df['body'] = df['close'] - df['open']
            df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
            df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
            
            # Candle type
            df['is_bullish'] = df['close'] > df['open']
            df['is_bearish'] = df['close'] < df['open']
            df['is_doji'] = abs(df['body']) < (df['range'] * 0.1)  # Body < 10% of range
            
            logger.info("Added basic features to DataFrame")
            return df
            
        except Exception as e:
            logger.error(f"Error adding basic features: {e}")
            return df
    
    @staticmethod
    def calculate_typical_price(df: pd.DataFrame) -> pd.Series:
        """
        Calculate typical price (HLC/3).
        
        Args:
            df: DataFrame with OHLC data
        
        Returns:
            Series with typical prices
        """
        return (df['high'] + df['low'] + df['close']) / 3
    
    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume Weighted Average Price.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            Series with VWAP values
        """
        try:
            typical_price = DataProcessor.calculate_typical_price(df)
            vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            return vwap
        except Exception as e:
            logger.error(f"Error calculating VWAP: {e}")
            return pd.Series(index=df.index)
    
    @staticmethod
    def detect_outliers(
        series: pd.Series,
        method: str = "iqr",
        threshold: float = 1.5
    ) -> pd.Series:
        """
        Detect outliers in a series.
        
        Args:
            series: Pandas series
            method: Detection method ("iqr" or "zscore")
            threshold: Threshold for outlier detection
        
        Returns:
            Boolean series indicating outliers
        """
        try:
            if method == "iqr":
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outliers = (series < lower_bound) | (series > upper_bound)
                
            elif method == "zscore":
                z_scores = np.abs((series - series.mean()) / series.std())
                outliers = z_scores > threshold
                
            else:
                raise ValueError(f"Unknown method: {method}")
            
            logger.info(f"Detected {outliers.sum()} outliers using {method} method")
            return outliers
            
        except Exception as e:
            logger.error(f"Error detecting outliers: {e}")
            return pd.Series(False, index=series.index)
    
    @staticmethod
    def fill_missing_bars(
        df: pd.DataFrame,
        freq: str = "30min"
    ) -> pd.DataFrame:
        """
        Fill missing bars with forward fill.
        
        Args:
            df: DataFrame with datetime index
            freq: Expected frequency
        
        Returns:
            DataFrame with filled missing bars
        """
        try:
            # Create complete time range
            full_range = pd.date_range(
                start=df.index.min(),
                end=df.index.max(),
                freq=freq
            )
            
            # Reindex and forward fill
            df_filled = df.reindex(full_range, method='ffill')
            
            filled_count = len(df_filled) - len(df)
            if filled_count > 0:
                logger.info(f"Filled {filled_count} missing bars")
            
            return df_filled
            
        except Exception as e:
            logger.error(f"Error filling missing bars: {e}")
            return df
    
    @staticmethod
    def export_to_csv(
        df: pd.DataFrame,
        filepath: str,
        symbol: str = ""
    ) -> bool:
        """
        Export DataFrame to CSV file.
        
        Args:
            df: DataFrame to export
            filepath: Output file path
            symbol: Symbol name for logging
        
        Returns:
            True if successful
        """
        try:
            df.to_csv(filepath)
            logger.info(f"Exported {symbol} data to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def load_from_csv(filepath: str) -> pd.DataFrame:
        """
        Load DataFrame from CSV file.
        
        Args:
            filepath: Input file path
        
        Returns:
            DataFrame with loaded data
        """
        try:
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
            logger.info(f"Loaded {len(df)} rows from {filepath}")
            return df
        except Exception as e:
            logger.error(f"Error loading from CSV: {e}")
            return pd.DataFrame()


# Helper functions
def get_market_hours(timezone: str = "US/Eastern") -> Dict[str, Any]:
    """
    Get market open/close times.
    
    Args:
        timezone: Market timezone
    
    Returns:
        Dictionary with market hours
    """
    return {
        'pre_market': {'start': '04:00', 'end': '09:30'},
        'regular': {'start': '09:30', 'end': '16:00'},
        'after_hours': {'start': '16:00', 'end': '20:00'},
        'timezone': timezone
    }


def is_market_open(current_time: Optional[datetime] = None) -> bool:
    """
    Check if market is currently open.
    
    Args:
        current_time: Time to check (default: now)
    
    Returns:
        True if market is open
    """
    if current_time is None:
        current_time = datetime.now()
    
    # Check if weekday (Mon-Fri)
    if current_time.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    
    # Check time (simple check, doesn't account for holidays)
    market_hours = get_market_hours()
    current_time_str = current_time.strftime("%H:%M")
    
    return (market_hours['regular']['start'] <= current_time_str <= 
            market_hours['regular']['end'])
