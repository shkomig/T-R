Add TWS Market Scanner integration to simple_live_dashboard.py:

1. Connect to IB Scanner API on startup
2. Subscribe to "TOP_PERC_GAIN" scanner (top % gainers in last 5 minutes)
3. Every 5 minutes, fetch top 20 gainers
4. Update self.symbols dynamically with these hot stocks
5. Keep MSTR and LCID always included (for SimpleMomentum strategy)
6. Display scanner results in dashboard output
7. Log when symbols list is updated

Requirements:
- Use ibapi.scanner module
- Filter results: price > $5, volume > 500K
- Max 25 symbols total (20 from scanner + 5 fixed)
- Handle scanner errors gracefully
- Add scanner status to dashboard header

Configuration:
- Scanner refresh interval: 5 minutes
- Instrument type: STK (stocks only)
- Location: US stocks
- Max results: 20

Expected outcome:
System will automatically trade the hottest stocks instead of waiting for signals from static list.