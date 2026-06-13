# SMART F&O ENGINE V3

## Objective

Build a high-quality intraday stock scanner for F&O stocks.

Focus on:

* Strong BUY setups
* Strong SELL setups
* Morning momentum
* Simple execution
* Stable signals

---

## Current Filters

### Stock Universe

* F&O Stocks Only
* CMP > ₹2500

### Timeframe

* 15 Minute

### Trend Filter

* EMA20

BUY:
Price > EMA20

SELL:
Price < EMA20

### Institutional Filter

* VWAP

BUY:
Price > VWAP

SELL:
Price < VWAP

### Participation Filter

* ROLV

Formula:

ROLV = Current Volume / Average Volume

Condition:

ROLV >= 1.8

### Volatility Filter

Use stock-specific daily volatility.

Used for:

* Stop Loss
* Target

---

## Signal Rules

### BUY

Price > EMA20

AND

Price > VWAP

AND

ROLV >= 1.8

### SELL

Price < EMA20

AND

Price < VWAP

AND

ROLV >= 1.8

---

## Signal Locking

Once signal appears:

Entry
SL
Target

must remain fixed for the entire day.

No changes after refresh.

---

## Scanner Window

Allowed:

09:30 AM to 12:30 PM

Ignore signals after 12:30 PM.

---

## Output Format

Stock
Action
Entry Time
Entry
SL
Target
RR

Example:

ABB.NS | BUY | 09:30-09:45 | 7269 | 7237 | 7333 | 1:2

---

## Future Improvements

### Phase 2

* OI Build-up
* OI Spurt
* Long Build-up
* Short Build-up

### Phase 3

* Trade Performance Tracking
* Win Rate Analysis
* Best Stock Ranking

---

## Current Deployment

GitHub Repository:
smart-fno-engine-v2

Deployment:
Streamlit Cloud

---

## Current Status

V3 Working

Features Active:

* EMA20
* VWAP
* ROLV
* Volatility SL/Target
* Signal Locking
* Streamlit Dashboard
* GitHub Deployment


# SMART F&O ENGINE PROJECT NOTES

## Date

13-Jun-2026

## Audit Findings

### Initial Result

Total Stocks = 48

Price > 2500 = 28

Trend Passed = 28

Tradeplan Passed = 0

Result:
No strong intraday setup found.

---

## Root Cause Investigation

Trend filter was not the issue.

Main bottleneck found inside:

* NIFTY Market Filter
* Intraday Tradeplan filters

After disabling NIFTY filter for audit:

Total Stocks = 48

Price > 2500 = 28

Trend Passed = 28

Tradeplan Passed = 23

Result:
Scanner logic is working.

Problem is trade selection, not trade generation.

---

## Key Learning

Previous assumption:

Need more filters.

Actual finding:

Need better ranking and selection.

---

## SMART F&O ENGINE V4 PLAN

### Objective

Show only:

* Market Decision
* Primary Trade
* Backup Trade

### Market Decision Logic

If BUY signals > SELL signals

→ BUY ONLY

If SELL signals > BUY signals

→ SELL ONLY

If difference is small

→ NO TRADE

---

### Stock Ranking

Rank using:

* ROLV
* EMA Distance
* VWAP Distance

---

### Output Format

MARKET DECISION

PRIMARY TRADE

BACKUP TRADE

---

### Trading Rules

Trade Primary first.

If Primary hits Target:
Stop Trading.

If Primary hits SL:
Take Backup Trade.

Maximum 2 trades per day.

No BUY and SELL together.

---

## Current Status

Version:
SMART F&O ENGINE V3.1 AUDIT

Status:
Working

Next Version:
SMART F&O ENGINE V4
