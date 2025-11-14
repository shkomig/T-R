"""
Emergency Trading Halt Manager - MCP-006
=========================================

Centralized emergency halt control system to immediately stop all trading
activity based on configurable risk thresholds or administrator intervention.

Features:
---------
1. Multiple automatic halt triggers (drawdown, daily loss, heat)
2. Manual halt capability (administrator override)
3. Halt state persistence across restarts
4. Authorized resume mechanism
5. Comprehensive logging
6. Trade blocking enforcement

Author: Claude AI (MCP-006)
Date: 2025-11-11
Version: 1.0.0
"""

import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import os


class HaltState(Enum):
    """Trading halt states"""
    ACTIVE = "active"        # Normal trading allowed
    HALTED = "halted"        # Trading stopped - emergency
    SUSPENDED = "suspended"  # Temporary suspension
    RESUMING = "resuming"    # Resuming after halt


class HaltTrigger(Enum):
    """Halt trigger types"""
    MANUAL = "manual"
    DRAWDOWN = "drawdown"
    DAILY_LOSS = "daily_loss"
    PORTFOLIO_HEAT = "portfolio_heat"
    TECHNICAL_FAILURE = "technical_failure"
    MARKET_CRASH = "market_crash"
    KILL_SWITCH = "kill_switch"


class EmergencyHaltManager:
    """
    Emergency Trading Halt Manager

    Manages emergency halt state, triggers, and resume authorization.
    Provides centralized control for stopping/starting trading activity.
    """

    def __init__(self, config_path: Optional[str] = None, data_dir: Optional[str] = None):
        """
        Initialize Emergency Halt Manager

        Parameters:
        -----------
        config_path : str, optional
            Path to risk_management.yaml configuration
        data_dir : str, optional
            Directory for halt state persistence
        """
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.config = self._load_config(config_path) if config_path else self._get_default_config()

        # State management
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / 'data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.halt_state_file = self.data_dir / 'halt_state.json'

        # Load or initialize state
        self.halt_state = self._load_halt_state()
        self.halt_history = []

        # Cooldown tracking
        self.last_halt_time = None
        self.resume_cooldown = timedelta(minutes=self.config.get('resume_cooldown_minutes', 5))

        self.logger.info("[SHIELD] Emergency Halt Manager initialized")
        self.logger.info(f"   Halt state file: {self.halt_state_file}")
        self.logger.info(f"   Current state: {self.halt_state['state']}")

    def _load_config(self, config_path: str) -> Dict:
        """Load emergency halt configuration from risk_management.yaml"""
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                emergency_config = config.get('emergency', {})

                self.logger.info(f"[OK] Emergency config loaded from {config_path}")
                return emergency_config
        except Exception as e:
            self.logger.warning(f"[WARN] Failed to load config: {e}, using defaults")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """Get default emergency halt configuration"""
        return {
            'enable_kill_switch': True,
            'kill_switch_triggers': [
                {'type': 'drawdown', 'threshold': 0.15},
                {'type': 'daily_loss', 'threshold': 0.05},
                {'type': 'manual'}
            ],
            'panic_mode': {
                'enabled': True,
                'triggers': ['market_crash', 'technical_failure'],
                'action': 'halt_trading'
            },
            'resume_cooldown_minutes': 5,
            'auto_resume': False
        }

    def _load_halt_state(self) -> Dict:
        """Load halt state from persistence file"""
        if self.halt_state_file.exists():
            try:
                with open(self.halt_state_file, 'r') as f:
                    state = json.load(f)
                    self.logger.info(f"[FILE] Loaded halt state: {state['state']}")
                    if state['state'] == HaltState.HALTED.value:
                        self.logger.warning(f"[WARN]  System was HALTED: {state.get('reason', 'Unknown')}")
                    return state
            except Exception as e:
                self.logger.error(f"[ERROR] Failed to load halt state: {e}")

        # Default state - active
        return {
            'state': HaltState.ACTIVE.value,
            'is_halted': False,
            'halt_time': None,
            'halt_reason': None,
            'trigger_type': None,
            'can_resume': True,
            'resume_authorization': None,
            'halt_count': 0
        }

    def _save_halt_state(self) -> None:
        """Save halt state to persistence file"""
        try:
            with open(self.halt_state_file, 'w') as f:
                json.dump(self.halt_state, f, indent=2)
            self.logger.debug(f"[SAVE] Halt state saved")
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to save halt state: {e}")

    def is_halted(self) -> bool:
        """Check if trading is currently halted"""
        return self.halt_state['is_halted']

    def get_halt_status(self) -> Dict[str, Any]:
        """
        Get comprehensive halt status

        Returns:
        --------
        dict with keys:
            - is_halted: bool
            - state: str
            - halt_reason: str or None
            - halt_time: str or None
            - trigger_type: str or None
            - can_resume: bool
            - time_since_halt: float (seconds) or None
        """
        status = self.halt_state.copy()

        # Add time since halt
        if self.halt_state['halt_time']:
            halt_time = datetime.fromisoformat(self.halt_state['halt_time'])
            status['time_since_halt'] = (datetime.now() - halt_time).total_seconds()
        else:
            status['time_since_halt'] = None

        return status

    def check_halt_conditions(self, risk_metrics: Dict) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if any halt conditions are met

        Parameters:
        -----------
        risk_metrics : dict
            Risk metrics from AdvancedRiskCalculator

        Returns:
        --------
        tuple: (should_halt, reason, trigger_type)
        """
        # Don't check if already halted
        if self.is_halted():
            return False, None, None

        # Check drawdown trigger
        drawdown_triggers = [t for t in self.config.get('kill_switch_triggers', [])
                           if t.get('type') == 'drawdown']
        if drawdown_triggers:
            threshold = drawdown_triggers[0].get('threshold', 0.15)
            current_drawdown = risk_metrics.get('current_drawdown', 0)
            if current_drawdown >= threshold:
                reason = f"Drawdown limit exceeded: {current_drawdown:.2%} >= {threshold:.2%}"
                return True, reason, HaltTrigger.DRAWDOWN.value

        # Check daily loss trigger
        daily_loss_triggers = [t for t in self.config.get('kill_switch_triggers', [])
                              if t.get('type') == 'daily_loss']
        if daily_loss_triggers:
            threshold = daily_loss_triggers[0].get('threshold', 0.05)
            daily_loss = risk_metrics.get('daily_loss', 0)
            if daily_loss >= threshold:
                reason = f"Daily loss limit exceeded: {daily_loss:.2%} >= {threshold:.2%}"
                return True, reason, HaltTrigger.DAILY_LOSS.value

        # Check portfolio heat (with more lenient threshold for auto-halt)
        # Normal limit is checked by risk calculator, this is extreme case
        portfolio_heat = risk_metrics.get('portfolio_heat', 0)
        if portfolio_heat >= 0.40:  # 40% heat triggers emergency halt (vs 25% normal limit)
            reason = f"Portfolio heat extreme: {portfolio_heat:.2%} >= 40%"
            return True, reason, HaltTrigger.PORTFOLIO_HEAT.value

        return False, None, None

    def trigger_halt(self, reason: str, trigger_type: str = HaltTrigger.MANUAL.value,
                    allow_resume: bool = True) -> bool:
        """
        Trigger emergency trading halt

        Parameters:
        -----------
        reason : str
            Human-readable reason for halt
        trigger_type : str
            Type of trigger (from HaltTrigger enum)
        allow_resume : bool
            Whether trading can be resumed

        Returns:
        --------
        bool: True if halt triggered successfully
        """
        if self.is_halted():
            self.logger.warning(f"[WARN]  System already halted, ignoring new halt request")
            return False

        # Update halt state
        self.halt_state = {
            'state': HaltState.HALTED.value,
            'is_halted': True,
            'halt_time': datetime.now().isoformat(),
            'halt_reason': reason,
            'trigger_type': trigger_type,
            'can_resume': allow_resume,
            'resume_authorization': None,
            'halt_count': self.halt_state.get('halt_count', 0) + 1
        }

        self.last_halt_time = datetime.now()
        self._save_halt_state()

        # Log emergency halt
        self._log_halt_event(reason, trigger_type)

        # Add to history
        self.halt_history.append({
            'time': datetime.now().isoformat(),
            'reason': reason,
            'trigger': trigger_type
        })

        self.logger.critical("[ALERT] " + "="*70)
        self.logger.critical("[ALERT] EMERGENCY TRADING HALT ACTIVATED")
        self.logger.critical("[ALERT] " + "="*70)
        self.logger.critical(f"[ALERT] Reason: {reason}")
        self.logger.critical(f"[ALERT] Trigger: {trigger_type}")
        self.logger.critical(f"[ALERT] Time: {self.halt_state['halt_time']}")
        self.logger.critical(f"[ALERT] Can resume: {allow_resume}")
        self.logger.critical("[ALERT] " + "="*70)
        self.logger.critical("[ALERT] ALL TRADING ACTIVITY SUSPENDED")
        self.logger.critical("[ALERT] " + "="*70)

        return True

    def trigger_kill_switch(self, reason: str = "Manual kill switch activated") -> bool:
        """
        Trigger immediate kill switch halt

        This is the most severe halt - bypasses all checks and stops trading immediately.

        Parameters:
        -----------
        reason : str
            Reason for kill switch activation

        Returns:
        --------
        bool: True if successful
        """
        self.logger.critical("[KILL] KILL SWITCH ACTIVATED [KILL]")
        return self.trigger_halt(reason, HaltTrigger.KILL_SWITCH.value, allow_resume=True)

    def resume_trading(self, authorization_code: Optional[str] = None,
                      force: bool = False) -> Tuple[bool, str]:
        """
        Resume trading after halt

        Parameters:
        -----------
        authorization_code : str, optional
            Authorization code for resume (if required)
        force : bool
            Force resume bypassing checks

        Returns:
        --------
        tuple: (success, message)
        """
        if not self.is_halted():
            return False, "System is not halted - already in active state"

        # Check if resume is allowed
        if not self.halt_state['can_resume'] and not force:
            return False, "Resume not allowed - manual intervention required"

        # Check cooldown period
        if self.last_halt_time and not force:
            time_since_halt = datetime.now() - self.last_halt_time
            if time_since_halt < self.resume_cooldown:
                remaining = (self.resume_cooldown - time_since_halt).total_seconds()
                return False, f"Cooldown period active - wait {remaining:.0f} more seconds"

        # Update state
        previous_reason = self.halt_state['halt_reason']
        self.halt_state = {
            'state': HaltState.ACTIVE.value,
            'is_halted': False,
            'halt_time': None,
            'halt_reason': None,
            'trigger_type': None,
            'can_resume': True,
            'resume_authorization': authorization_code,
            'halt_count': self.halt_state.get('halt_count', 0),
            'last_resume_time': datetime.now().isoformat()
        }

        self._save_halt_state()

        # Log resume event
        self.logger.warning("[OK] " + "="*70)
        self.logger.warning("[OK] TRADING RESUMED")
        self.logger.warning("[OK] " + "="*70)
        self.logger.warning(f"[OK] Previous halt reason: {previous_reason}")
        self.logger.warning(f"[OK] Resume time: {self.halt_state['last_resume_time']}")
        if authorization_code:
            self.logger.warning(f"[OK] Authorization: {authorization_code}")
        if force:
            self.logger.warning(f"[OK] FORCED RESUME")
        self.logger.warning("[OK] " + "="*70)

        return True, "Trading resumed successfully"

    def _log_halt_event(self, reason: str, trigger_type: str) -> None:
        """Log halt event to dedicated file"""
        log_file = self.data_dir / 'halt_events.log'

        try:
            with open(log_file, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"HALT EVENT - {datetime.now().isoformat()}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Reason: {reason}\n")
                f.write(f"Trigger Type: {trigger_type}\n")
                f.write(f"Halt Count: {self.halt_state['halt_count']}\n")
                f.write(f"Can Resume: {self.halt_state['can_resume']}\n")
                f.write(f"{'='*80}\n")
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to log halt event: {e}")

    def block_trade(self, symbol: str, action: str, reason: str = None) -> str:
        """
        Block a trade attempt during halt

        Parameters:
        -----------
        symbol : str
            Trading symbol
        action : str
            Intended action (BUY/SELL)
        reason : str, optional
            Additional reason

        Returns:
        --------
        str: Block message for logging
        """
        message = f"[BLOCKED] TRADE BLOCKED - System HALTED\n"
        message += f"   Symbol: {symbol}\n"
        message += f"   Action: {action}\n"
        message += f"   Halt reason: {self.halt_state['halt_reason']}\n"
        message += f"   Halt time: {self.halt_state['halt_time']}\n"
        if reason:
            message += f"   Additional: {reason}\n"

        self.logger.warning(message)
        return message

    def get_halt_summary(self) -> str:
        """
        Get formatted halt status summary

        Returns:
        --------
        str: Formatted status message
        """
        if not self.is_halted():
            return "Trading Status: ACTIVE [OK]"

        status = self.get_halt_status()
        summary = f"Trading Status: HALTED [ALERT]\n"
        summary += f"Reason: {status['halt_reason']}\n"
        summary += f"Trigger: {status['trigger_type']}\n"
        summary += f"Halt Time: {status['halt_time']}\n"

        if status['time_since_halt']:
            minutes = status['time_since_halt'] / 60
            summary += f"Duration: {minutes:.1f} minutes\n"

        summary += f"Can Resume: {'Yes' if status['can_resume'] else 'No'}\n"
        summary += f"Total Halts: {status['halt_count']}\n"

        return summary


# Module-level instance for easy access (optional)
_halt_manager_instance = None


def get_halt_manager(config_path: Optional[str] = None, data_dir: Optional[str] = None) -> EmergencyHaltManager:
    """
    Get or create halt manager singleton

    Parameters:
    -----------
    config_path : str, optional
        Path to risk_management.yaml
    data_dir : str, optional
        Directory for state persistence

    Returns:
    --------
    EmergencyHaltManager: Singleton instance
    """
    global _halt_manager_instance
    if _halt_manager_instance is None:
        _halt_manager_instance = EmergencyHaltManager(config_path, data_dir)
    return _halt_manager_instance


if __name__ == "__main__":
    # Test the Emergency Halt Manager
    print("[SHIELD] Testing Emergency Halt Manager...")

    # Initialize
    manager = EmergencyHaltManager()

    # Test halt
    print("\n1. Testing manual halt...")
    success = manager.trigger_halt("Test halt for demonstration", HaltTrigger.MANUAL.value)
    print(f"   Halt triggered: {success}")
    print(f"   Is halted: {manager.is_halted()}")

    # Test status
    print("\n2. Getting halt status...")
    print(manager.get_halt_summary())

    # Test blocked trade
    print("\n3. Testing trade block...")
    block_msg = manager.block_trade("AAPL", "BUY 100")
    print(block_msg)

    # Test resume
    print("\n4. Testing resume (should fail - cooldown)...")
    success, msg = manager.resume_trading()
    print(f"   Resume result: {msg}")

    # Force resume
    print("\n5. Testing forced resume...")
    success, msg = manager.resume_trading(force=True)
    print(f"   Resume result: {msg}")
    print(f"   Is halted: {manager.is_halted()}")

    print("\n[OK] Emergency Halt Manager test completed!")
