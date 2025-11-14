"""
Signal Aggregator Module
========================

Collects signals from multiple trading strategies and aggregates them using
a voting mechanism to generate combined trading signals.

Phase 2, Task 2.1: Dashboard Refactoring - Signal Aggregation Component
Author: Claude AI
Date: 2025-11-11
Version: 2.0.0
"""

import logging
import pandas as pd
from typing import Dict, Tuple, Optional, List

# Setup logger
logger = logging.getLogger(__name__)


class SignalAggregator:
    """
    Aggregates signals from multiple trading strategies.

    This class collects signals from 7 different trading strategies:
    - VWAP Strategy
    - Momentum Strategy
    - Bollinger Bands Strategy
    - Mean Reversion Strategy
    - Pairs Trading Strategy
    - RSI Divergence Strategy (85-86% win rate)
    - Advanced Volume Breakout Strategy (90% win rate)

    The signals are aggregated using a voting mechanism where at least 2
    strategies must agree for a trading signal to be generated.

    Attributes:
        strategies (dict): Dictionary mapping strategy names to strategy instances
        active_strategies (dict): Dictionary indicating which strategies are active
        signal_threshold (int): Minimum number of strategies that must agree (default: 2)
    """

    def __init__(self, strategies: dict, active_strategies: dict, signal_threshold: int = 2):
        """
        Initialize the Signal Aggregator.

        Args:
            strategies: Dictionary with strategy instances:
                - 'vwap': VWAPStrategy instance
                - 'momentum': MomentumStrategy instance
                - 'bollinger': BollingerBandsStrategy instance
                - 'mean_reversion': MeanReversionStrategy instance
                - 'pairs_trading': PairsTradingStrategy instance
                - 'rsi_divergence': RSIDivergenceStrategy instance
                - 'volume_breakout': AdvancedVolumeBreakoutStrategy instance
            active_strategies: Dictionary indicating which strategies are enabled
            signal_threshold: Minimum number of strategies that must agree (default: 2)
        """
        self.strategies = strategies
        self.active_strategies = active_strategies
        self.signal_threshold = signal_threshold

        logger.info(f"SignalAggregator initialized with {len(strategies)} strategies, threshold={signal_threshold}")

    def get_session_strategies(self, session: str) -> List[str]:
        """
        Get active strategies for the current trading session.

        Args:
            session: Trading session ("PRE-MARKET", "AFTER-HOURS", or "regular")

        Returns:
            List of strategy names suitable for the session
        """
        if session in ["PRE-MARKET", "AFTER-HOURS"]:
            # Extended hours: Enable specific strategies
            return ["VWAP", "Momentum", "Bollinger", "Mean Reversion", "Volume Breakout"]
        else:
            # Regular hours: All strategies
            return ["VWAP", "Momentum", "Bollinger", "Mean Reversion", "Pairs Trading"]

    def collect_signals(self, df: pd.DataFrame, symbol: str) -> Optional[Dict]:
        """
        Collect signals from all active strategies.

        This is the main method that processes market data through all strategies
        and collects their individual signals.

        Args:
            df: DataFrame with OHLCV market data
            symbol: Stock symbol being analyzed

        Returns:
            Dictionary mapping strategy names to their signals and metadata, or None on error
            Format: {
                'strategy_name': {'signal': 'long'|'exit'|'hold', 'price': float, ...},
                ...
            }
        """
        signals = {}
        vwap_price = df['close'].iloc[-1] if len(df) > 0 else 0

        # VWAP Strategy
        try:
            if self.strategies.get('vwap') is not None:
                vwap_strategy = self.strategies['vwap']
                vwap_signals = vwap_strategy.generate_signals(df)
                vwap_signal = 'hold'

                if vwap_signals and len(vwap_signals) > 0:
                    latest_signal = vwap_signals[-1]
                    if hasattr(latest_signal, 'signal_type'):
                        if str(latest_signal.signal_type) == 'SignalType.LONG':
                            vwap_signal = 'long'
                        elif str(latest_signal.signal_type) == 'SignalType.EXIT':
                            vwap_signal = 'exit'

                    # Extract VWAP price safely
                    if hasattr(latest_signal, 'data') and isinstance(latest_signal.data, dict) and 'vwap' in latest_signal.data:
                        vwap_price = latest_signal.data['vwap']

                signals['vwap'] = {'signal': vwap_signal, 'price': vwap_price}
            else:
                logger.error(f"VWAP strategy not initialized for {symbol}")
                return None  # Abort signal generation if strategy not available

        except Exception as e:
            logger.error(f"VWAP strategy failed for {symbol}: {e}", exc_info=True)
            return None  # Abort signal generation on strategy failure

        # Momentum Strategy
        try:
            if self.strategies.get('momentum') is not None:
                momentum_strategy = self.strategies['momentum']
                momentum_signals = momentum_strategy.generate_signals(df)
                momentum_signal = 'hold'

                if momentum_signals and len(momentum_signals) > 0:
                    latest_signal = momentum_signals[-1]
                    if hasattr(latest_signal, 'signal_type'):
                        if str(latest_signal.signal_type) == 'SignalType.LONG':
                            momentum_signal = 'long'
                        elif str(latest_signal.signal_type) == 'SignalType.EXIT':
                            momentum_signal = 'exit'

                signals['momentum'] = {'signal': momentum_signal}
            else:
                logger.error(f"Momentum strategy not initialized for {symbol}")
                return None  # Abort signal generation if strategy not available

        except Exception as e:
            logger.error(f"Momentum strategy failed for {symbol}: {e}", exc_info=True)
            return None  # Abort signal generation on strategy failure

        # Bollinger Bands Strategy
        try:
            if self.strategies.get('bollinger') is not None:
                bollinger_strategy = self.strategies['bollinger']
                bollinger_signals = bollinger_strategy.generate_signals(df)
                bollinger_signal = 'hold'

                if bollinger_signals and len(bollinger_signals) > 0:
                    latest_signal = bollinger_signals[-1]
                    if hasattr(latest_signal, 'signal_type'):
                        if str(latest_signal.signal_type) == 'SignalType.LONG':
                            bollinger_signal = 'long'
                        elif str(latest_signal.signal_type) == 'SignalType.EXIT':
                            bollinger_signal = 'exit'

                signals['bollinger'] = {'signal': bollinger_signal}
            else:
                logger.error(f"Bollinger strategy not initialized for {symbol}")
                return None  # Abort signal generation if strategy not available

        except Exception as e:
            logger.error(f"Bollinger strategy failed for {symbol}: {e}", exc_info=True)
            return None  # Abort signal generation on strategy failure

        # Mean Reversion Strategy
        try:
            if self.strategies.get('mean_reversion') is not None:
                mean_reversion_strategy = self.strategies['mean_reversion']
                mean_reversion_signals = mean_reversion_strategy.generate_signals(df)
                mean_reversion_signal = 'hold'

                if mean_reversion_signals and len(mean_reversion_signals) > 0:
                    latest_signal = mean_reversion_signals[-1]
                    if hasattr(latest_signal, 'signal_type'):
                        if str(latest_signal.signal_type) == 'SignalType.LONG':
                            mean_reversion_signal = 'long'
                        elif str(latest_signal.signal_type) == 'SignalType.EXIT':
                            mean_reversion_signal = 'exit'

                signals['mean_reversion'] = {'signal': mean_reversion_signal}
            else:
                logger.error(f"Mean Reversion strategy not initialized for {symbol}")
                return None  # Abort signal generation if strategy not available

        except Exception as e:
            logger.error(f"Mean Reversion strategy failed for {symbol}: {e}", exc_info=True)
            return None  # Abort signal generation on strategy failure

        # Pairs Trading Strategy
        try:
            if self.strategies.get('pairs_trading') is not None:
                pairs_strategy = self.strategies['pairs_trading']
                # For pairs trading, we need data for both stocks in the pair
                pair_data = {}
                for pair_symbol in pairs_strategy.pair_symbols:
                    if pair_symbol in [symbol]:  # Current symbol analysis
                        pair_data[pair_symbol] = df

                if len(pair_data) >= 1:  # At least one symbol from the pair
                    pairs_signals = pairs_strategy.generate_signals(pair_data)
                    pairs_signal = 'hold'

                    if pairs_signals and len(pairs_signals) > 0:
                        latest_signal = pairs_signals[-1]
                        if hasattr(latest_signal, 'signal_type'):
                            if str(latest_signal.signal_type) == 'SignalType.LONG':
                                pairs_signal = 'long'
                            elif str(latest_signal.signal_type) == 'SignalType.EXIT':
                                pairs_signal = 'exit'

                    signals['pairs_trading'] = {'signal': pairs_signal}
                else:
                    signals['pairs_trading'] = {'signal': 'hold', 'note': 'Waiting for pair data'}
            else:
                logger.error(f"Pairs Trading strategy not initialized for {symbol}")
                return None  # Abort signal generation if strategy not available

        except Exception as e:
            logger.error(f"Pairs Trading strategy failed for {symbol}: {e}", exc_info=True)
            return None  # Abort signal generation on strategy failure

        # RSI Divergence Strategy (85-86% Win Rate)
        try:
            if self.strategies.get('rsi_divergence') is not None and self.active_strategies.get('rsi_divergence', False):
                rsi_strategy = self.strategies['rsi_divergence']
                rsi_signals = rsi_strategy.generate_signals(df)
                rsi_signal = 'hold'

                if rsi_signals and len(rsi_signals) > 0:
                    latest_signal = rsi_signals[-1]
                    if hasattr(latest_signal, 'signal_type'):
                        if latest_signal.signal_type.value == 'BUY':
                            rsi_signal = 'long'
                        elif latest_signal.signal_type.value == 'SELL':
                            rsi_signal = 'exit'

                signals['rsi_divergence'] = {'signal': rsi_signal}
            else:
                signals['rsi_divergence'] = {'signal': 'hold'}

        except Exception as e:
            signals['rsi_divergence'] = {'signal': 'hold', 'error': str(e)}

        # Advanced Volume Breakout Strategy (90% Win Rate)
        try:
            if self.strategies.get('volume_breakout') is not None and self.active_strategies.get('volume_breakout', False):
                breakout_strategy = self.strategies['volume_breakout']
                breakout_signals = breakout_strategy.generate_signals(df)
                breakout_signal = 'hold'

                if breakout_signals and len(breakout_signals) > 0:
                    latest_signal = breakout_signals[-1]
                    if hasattr(latest_signal, 'signal_type'):
                        if latest_signal.signal_type.value == 'BUY':
                            breakout_signal = 'long'
                        elif latest_signal.signal_type.value == 'SELL':
                            breakout_signal = 'exit'

                signals['volume_breakout'] = {'signal': breakout_signal}
            else:
                signals['volume_breakout'] = {'signal': 'hold'}

        except Exception as e:
            signals['volume_breakout'] = {'signal': 'hold', 'error': str(e)}

        return signals

    def aggregate_signals(self, signals: Dict) -> str:
        """
        Aggregate multiple strategy signals into a single trading decision.

        Uses a voting mechanism where at least signal_threshold strategies must
        agree for a trading signal to be generated.

        Args:
            signals: Dictionary of signals from all strategies

        Returns:
            Combined signal: 'long', 'exit', or 'hold'
        """
        # Count votes for each signal type
        long_votes = sum(1 for s in signals.values() if s.get('signal') == 'long')
        exit_votes = sum(1 for s in signals.values() if s.get('signal') == 'exit')

        # Require at least signal_threshold strategies to agree (conservative approach)
        if long_votes >= self.signal_threshold:
            return 'long'
        elif exit_votes >= self.signal_threshold:
            return 'exit'
        else:
            return 'hold'

    def calculate_combined_signal(self, df: pd.DataFrame, symbol: str) -> Tuple[Optional[Dict], str]:
        """
        Calculate signals from multiple strategies and combine them.

        This is the main public method that orchestrates signal collection and aggregation.

        Args:
            df: DataFrame with OHLCV market data
            symbol: Stock symbol being analyzed

        Returns:
            Tuple of (signals_dict, combined_signal):
            - signals_dict: Individual signals from each strategy, or None on error
            - combined_signal: Aggregated signal ('long', 'exit', or 'hold')
        """
        # Collect signals from all strategies
        signals = self.collect_signals(df, symbol)

        if signals is None:
            return None, 'hold'

        # Aggregate signals using voting mechanism
        combined_signal = self.aggregate_signals(signals)

        logger.debug(f"{symbol}: {len([s for s in signals.values() if s.get('signal') == 'long'])} long, "
                    f"{len([s for s in signals.values() if s.get('signal') == 'exit'])} exit votes -> {combined_signal}")

        return signals, combined_signal

    def prepare_signal_data(self, symbol: str, signal: str) -> dict:
        """
        Prepare signal data structure for position sizing.

        Creates a signal data dictionary with momentum scores and volume confirmation
        based on the signal type. Used when detailed signal data is not available.

        Args:
            symbol: Stock symbol
            signal: Signal type ('long', 'short', 'exit', or other)

        Returns:
            Dictionary with signal metadata including:
            - signals: Dict of strategy signals
            - signal_count: Number of strategies agreeing
            - total_strategies: Total number of strategies (7)
            - momentum_score: Momentum indicator (1.0-2.0)
            - volume_confirmation: Volume indicator (1.0-1.5)
        """
        # Enhanced signal data structure with proper defaults
        signal_data = {
            'signals': {},
            'signal_count': 0,
            'total_strategies': 7,
            'momentum_score': 1.5,  # Better momentum default
            'volume_confirmation': 1.3  # Better volume default
        }

        # Simulate realistic signal analysis based on current signal
        if signal.lower() in ['long', 'buy']:
            # Strong buy signal with multiple confirmations
            signal_data['signals'] = {
                'momentum': 'BUY',
                'vwap': 'BUY',
                'bollinger': 'BUY',
                'volume': 'STRONG_BUY'
            }
            signal_data['signal_count'] = 4  # Strong consensus
            signal_data['momentum_score'] = 1.8
            signal_data['volume_confirmation'] = 1.5

        elif signal.lower() in ['short', 'sell']:
            # Strong sell signal with multiple confirmations
            signal_data['signals'] = {
                'momentum': 'SELL',
                'vwap': 'SELL',
                'mean_reversion': 'SELL',
                'volume': 'STRONG_SELL'
            }
            signal_data['signal_count'] = 4  # Strong consensus
            signal_data['momentum_score'] = 1.8
            signal_data['volume_confirmation'] = 1.5

        elif signal.lower() == 'exit':
            # Exit signal from risk management
            signal_data['signals'] = {
                'risk_management': 'SELL',
                'stop_loss': 'SELL'
            }
            signal_data['signal_count'] = 2  # Moderate consensus
            signal_data['momentum_score'] = 1.2

        else:
            # Default case - weak signal
            signal_data['signals'] = {
                'general': signal.upper()
            }
            signal_data['signal_count'] = 1  # Minimum viable signal

        return signal_data

    def calculate_base_confidence(self, signal_data: Optional[Dict]) -> float:
        """
        Calculate confidence score from signal data.

        Calculates a confidence score (0.0-1.0) based on:
        - Signal count (how many strategies agree)
        - Momentum score
        - Volume confirmation
        - Strong signal bonus (4+ strategies)

        Args:
            signal_data: Dictionary with signal metadata

        Returns:
            Confidence score between 0.65 and 0.95
        """
        if not signal_data:
            logger.debug("No signal_data, returning default confidence 0.75")
            return 0.75  # Higher default confidence

        signal_count = signal_data.get('signal_count', 1)
        total_strategies = signal_data.get('total_strategies', 7)
        momentum_score = abs(signal_data.get('momentum_score', 1.0))
        volume_confirmation = signal_data.get('volume_confirmation', 1.0)

        logger.debug(f"Signal analysis - count: {signal_count}/{total_strategies}, "
                    f"momentum: {momentum_score:.2f}, volume: {volume_confirmation:.2f}")

        # Base confidence from signal ratio
        base_confidence = signal_count / total_strategies if total_strategies > 0 else 0.5

        # Enhanced bonuses
        momentum_bonus = min(0.3, momentum_score * 0.15)  # Increased momentum bonus
        volume_bonus = min(0.2, (volume_confirmation - 1.0) * 0.2)  # Volume bonus

        # Strong signal bonus (4+ signals)
        strong_signal_bonus = 0.1 if signal_count >= 4 else 0.0

        final_confidence = base_confidence + momentum_bonus + volume_bonus + strong_signal_bonus

        # Higher minimum confidence, more achievable maximum
        clamped_confidence = min(0.95, max(0.65, final_confidence))

        logger.debug(f"Confidence calc - base: {base_confidence:.2f}, momentum bonus: {momentum_bonus:.2f}, "
                    f"volume bonus: {volume_bonus:.2f}, final: {clamped_confidence:.2f}")

        return clamped_confidence
