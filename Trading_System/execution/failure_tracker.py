"""
Failure Tracking System - Task 1.6 (MCP Phase 1)
================================================

Tracks strategy failures and triggers emergency halt after consecutive failures.
Implements proper error handling without fallbacks.

Features:
---------
1. SignalGenerationFailure class for explicit failure reporting
2. Failure counter with configurable threshold
3. Automatic emergency halt trigger
4. Failure history tracking
5. Reset on successful signal generation

Author: Claude AI (Phase 1 - Task 1.6)
Date: 2025-11-11
Version: 1.0.0
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class FailureType(Enum):
    """Types of failures that can occur"""
    STRATEGY_ERROR = "strategy_error"
    DATA_ERROR = "data_error"
    EXECUTION_ERROR = "execution_error"
    CONNECTION_ERROR = "connection_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class SignalGenerationFailure:
    """
    Represents a failed signal generation attempt.

    This class encapsulates all information about a strategy failure,
    replacing random signal generation with explicit failure state.
    """
    strategy_name: str
    symbol: str
    error_message: str
    failure_type: FailureType
    timestamp: datetime = field(default_factory=datetime.now)
    stack_trace: Optional[str] = None
    additional_context: Dict = field(default_factory=dict)

    def __str__(self) -> str:
        """Human-readable failure description"""
        return (
            f"[FAILURE] {self.strategy_name} failed for {self.symbol}\n"
            f"   Type: {self.failure_type.value}\n"
            f"   Time: {self.timestamp.isoformat()}\n"
            f"   Error: {self.error_message}"
        )

    def to_dict(self) -> Dict:
        """Convert to dictionary for logging/storage"""
        return {
            'strategy': self.strategy_name,
            'symbol': self.symbol,
            'error': self.error_message,
            'type': self.failure_type.value,
            'timestamp': self.timestamp.isoformat(),
            'stack_trace': self.stack_trace,
            'context': self.additional_context
        }


class FailureTracker:
    """
    Tracks failures and triggers emergency halt when threshold exceeded.

    Implements the "fail fast" pattern from Task 1.6:
    - No fallbacks to random data
    - Explicit failure states
    - Automatic halt on consecutive failures
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        reset_window: timedelta = timedelta(minutes=5),
        halt_callback: Optional[callable] = None
    ):
        """
        Initialize failure tracker.

        Parameters:
        -----------
        failure_threshold : int
            Number of consecutive failures before triggering halt (default: 3)
        reset_window : timedelta
            Time window after which counter resets if no failures (default: 5 min)
        halt_callback : callable, optional
            Function to call when halt threshold reached
        """
        self.failure_threshold = failure_threshold
        self.reset_window = reset_window
        self.halt_callback = halt_callback

        # Failure tracking
        self.consecutive_failures = 0
        self.total_failures = 0
        self.failure_history: List[SignalGenerationFailure] = []
        self.last_failure_time: Optional[datetime] = None
        self.last_success_time: Optional[datetime] = None

        # Strategy-specific tracking
        self.strategy_failures: Dict[str, int] = {}
        self.symbol_failures: Dict[str, int] = {}

        # State
        self.halt_triggered = False
        self.halt_reason = None

        self.logger = logging.getLogger(__name__)
        self.logger.info("[TRACKER] Failure Tracker initialized")
        self.logger.info(f"   Failure threshold: {failure_threshold} consecutive failures")
        self.logger.info(f"   Reset window: {reset_window.total_seconds()} seconds")

    def record_failure(
        self,
        strategy_name: str,
        symbol: str,
        error: Exception,
        failure_type: FailureType = FailureType.STRATEGY_ERROR,
        additional_context: Optional[Dict] = None
    ) -> SignalGenerationFailure:
        """
        Record a failure event.

        Parameters:
        -----------
        strategy_name : str
            Name of the strategy that failed
        symbol : str
            Trading symbol
        error : Exception
            The exception that occurred
        failure_type : FailureType
            Type of failure
        additional_context : dict, optional
            Additional context information

        Returns:
        --------
        SignalGenerationFailure: The failure object
        """
        # Create failure object
        failure = SignalGenerationFailure(
            strategy_name=strategy_name,
            symbol=symbol,
            error_message=str(error),
            failure_type=failure_type,
            stack_trace=self._get_stack_trace(error),
            additional_context=additional_context or {}
        )

        # Update counters
        self.consecutive_failures += 1
        self.total_failures += 1
        self.last_failure_time = datetime.now()

        # Update strategy-specific tracking
        self.strategy_failures[strategy_name] = \
            self.strategy_failures.get(strategy_name, 0) + 1
        self.symbol_failures[symbol] = \
            self.symbol_failures.get(symbol, 0) + 1

        # Add to history (keep last 100)
        self.failure_history.append(failure)
        if len(self.failure_history) > 100:
            self.failure_history = self.failure_history[-100:]

        # Log the failure
        self.logger.error(str(failure))
        if failure.stack_trace:
            self.logger.debug(f"Stack trace:\n{failure.stack_trace}")

        # Check if threshold exceeded
        if self.consecutive_failures >= self.failure_threshold and not self.halt_triggered:
            self._trigger_emergency_halt(failure)

        return failure

    def record_success(self, strategy_name: str, symbol: str) -> None:
        """
        Record a successful signal generation.

        Resets consecutive failure counter on success.

        Parameters:
        -----------
        strategy_name : str
            Name of the strategy
        symbol : str
            Trading symbol
        """
        self.consecutive_failures = 0
        self.last_success_time = datetime.now()

        self.logger.debug(
            f"[OK] Success recorded: {strategy_name} for {symbol} "
            f"(consecutive failures reset to 0)"
        )

    def _trigger_emergency_halt(self, triggering_failure: SignalGenerationFailure) -> None:
        """
        Trigger emergency halt due to excessive failures.

        Parameters:
        -----------
        triggering_failure : SignalGenerationFailure
            The failure that triggered the halt
        """
        self.halt_triggered = True
        self.halt_reason = (
            f"Consecutive failure threshold exceeded: "
            f"{self.consecutive_failures} >= {self.failure_threshold}"
        )

        self.logger.critical("[HALT] " + "="*70)
        self.logger.critical("[HALT] EMERGENCY HALT TRIGGERED BY FAILURE TRACKER")
        self.logger.critical("[HALT] " + "="*70)
        self.logger.critical(f"[HALT] Consecutive failures: {self.consecutive_failures}")
        self.logger.critical(f"[HALT] Threshold: {self.failure_threshold}")
        self.logger.critical(f"[HALT] Triggering failure:")
        self.logger.critical(f"[HALT]   Strategy: {triggering_failure.strategy_name}")
        self.logger.critical(f"[HALT]   Symbol: {triggering_failure.symbol}")
        self.logger.critical(f"[HALT]   Error: {triggering_failure.error_message}")
        self.logger.critical("[HALT] " + "="*70)

        # Call halt callback if provided
        if self.halt_callback:
            try:
                self.halt_callback(self.halt_reason, triggering_failure)
            except Exception as e:
                self.logger.error(f"[ERROR] Halt callback failed: {e}")

    def should_reset(self) -> bool:
        """
        Check if failure counter should be reset based on time window.

        Returns:
        --------
        bool: True if enough time has passed since last failure
        """
        if self.last_failure_time is None:
            return False

        time_since_failure = datetime.now() - self.last_failure_time
        return time_since_failure >= self.reset_window

    def reset(self) -> None:
        """Reset failure counters (manual reset)"""
        self.consecutive_failures = 0
        self.logger.info("[RESET] Failure counter manually reset to 0")

    def get_status(self) -> Dict:
        """
        Get current failure tracking status.

        Returns:
        --------
        dict: Status information
        """
        recent_failures = self.failure_history[-10:] if self.failure_history else []

        return {
            'consecutive_failures': self.consecutive_failures,
            'total_failures': self.total_failures,
            'failure_threshold': self.failure_threshold,
            'halt_triggered': self.halt_triggered,
            'halt_reason': self.halt_reason,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
            'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None,
            'strategy_failures': self.strategy_failures,
            'symbol_failures': self.symbol_failures,
            'recent_failures': [f.to_dict() for f in recent_failures]
        }

    def get_failure_summary(self) -> str:
        """
        Get formatted failure summary.

        Returns:
        --------
        str: Formatted summary
        """
        status = self.get_status()

        summary = f"Failure Tracker Status\n"
        summary += f"{'='*50}\n"
        summary += f"Consecutive Failures: {status['consecutive_failures']}/{status['failure_threshold']}\n"
        summary += f"Total Failures: {status['total_failures']}\n"

        if status['halt_triggered']:
            summary += f"\n[ALERT] HALT TRIGGERED\n"
            summary += f"Reason: {status['halt_reason']}\n"

        if status['strategy_failures']:
            summary += f"\nFailures by Strategy:\n"
            for strategy, count in sorted(
                status['strategy_failures'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                summary += f"  {strategy}: {count}\n"

        return summary

    def _get_stack_trace(self, error: Exception) -> str:
        """Extract stack trace from exception"""
        import traceback
        return ''.join(traceback.format_exception(type(error), error, error.__traceback__))

    def clear_history(self) -> None:
        """Clear failure history (for testing/maintenance)"""
        self.failure_history.clear()
        self.strategy_failures.clear()
        self.symbol_failures.clear()
        self.logger.info("[CLEAR] Failure history cleared")


# Module-level singleton for easy access
_failure_tracker_instance: Optional[FailureTracker] = None


def get_failure_tracker(
    failure_threshold: int = 3,
    reset_window: timedelta = timedelta(minutes=5),
    halt_callback: Optional[callable] = None
) -> FailureTracker:
    """
    Get or create failure tracker singleton.

    Parameters:
    -----------
    failure_threshold : int
        Number of consecutive failures before halt
    reset_window : timedelta
        Time window for counter reset
    halt_callback : callable, optional
        Function to call on halt trigger

    Returns:
    --------
    FailureTracker: Singleton instance
    """
    global _failure_tracker_instance
    if _failure_tracker_instance is None:
        _failure_tracker_instance = FailureTracker(
            failure_threshold=failure_threshold,
            reset_window=reset_window,
            halt_callback=halt_callback
        )
    return _failure_tracker_instance


if __name__ == "__main__":
    # Test the failure tracker
    print("[TRACKER] Testing Failure Tracker...")

    # Initialize
    tracker = FailureTracker(failure_threshold=3)

    # Test 1: Record some failures
    print("\n1. Recording failures...")
    for i in range(2):
        try:
            raise ValueError(f"Test error {i+1}")
        except Exception as e:
            failure = tracker.record_failure(
                strategy_name="TestStrategy",
                symbol="AAPL",
                error=e,
                failure_type=FailureType.STRATEGY_ERROR
            )
            print(f"   Recorded failure {i+1}, consecutive: {tracker.consecutive_failures}")

    # Test 2: Record success (should reset)
    print("\n2. Recording success...")
    tracker.record_success("TestStrategy", "AAPL")
    print(f"   Consecutive failures after success: {tracker.consecutive_failures}")

    # Test 3: Trigger halt threshold
    print("\n3. Triggering halt threshold...")
    for i in range(3):
        try:
            raise ValueError(f"Critical error {i+1}")
        except Exception as e:
            tracker.record_failure(
                strategy_name="TestStrategy",
                symbol="AAPL",
                error=e
            )

    # Test 4: Get status
    print("\n4. Status summary:")
    print(tracker.get_failure_summary())

    print("\n[OK] Failure Tracker test completed!")
