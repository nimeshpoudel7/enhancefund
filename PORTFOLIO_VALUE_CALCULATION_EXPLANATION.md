# Portfolio Value Calculation Explanation

## Current Formula

```
Portfolio Value = Total Invested + Actual Returns + Expected Returns
```

## Detailed Breakdown

### 1. **Total Invested** (Principal)
- Sum of all investment amounts you've made
- Example: If you invested $1,000 in Loan A and $2,000 in Loan B, Total Invested = $3,000

### 2. **Actual Returns** (Realized Gains)
- Returns from investments that have been **closed/completed**
- Only counted if `investment.net_return` has a value
- Example: Loan A closed and you received $50 in returns → Actual Returns = $50

### 3. **Expected Returns** (Projected Gains)
- Projected returns from investments that are still **open/active**
- Only calculated for investments where `investment.net_return` is NULL/empty
- Formula: `Investment Amount × (Interest Rate × 0.97) / 100`
- The `× 0.97` factor accounts for a 3% platform fee
- Example: 
  - Investment: $1,000
  - Interest Rate: 10%
  - Expected Return = $1,000 × (10 × 0.97) / 100 = $97

## Example Calculation

### Scenario:
- **Investment 1**: $1,000 in Loan A (10% interest, CLOSED, received $97 return)
- **Investment 2**: $2,000 in Loan B (8% interest, OPEN, no return yet)
- **Investment 3**: $500 in Loan C (12% interest, OPEN, no return yet)

### Calculation:
```
Total Invested = $1,000 + $2,000 + $500 = $3,500

Actual Returns = $97 (only from Investment 1, which is closed)

Expected Returns:
  - Investment 2: $2,000 × (8 × 0.97) / 100 = $155.20
  - Investment 3: $500 × (12 × 0.97) / 100 = $58.20
  Total Expected = $155.20 + $58.20 = $213.40

Portfolio Value = $3,500 + $97 + $213.40 = $3,810.40
```

## Important Notes

1. **Mutually Exclusive**: An investment either has actual returns OR expected returns, never both
2. **Platform Fee**: The 0.97 multiplier accounts for a 3% platform fee (you get 97% of the interest)
3. **Real-time**: Expected returns are calculated based on current interest rates
4. **Actual vs Expected**: 
   - Actual returns = money you've already received
   - Expected returns = money you're projected to receive (not guaranteed)

## Potential Issues with Current Implementation

### Issue 1: Interest Rate Calculation
The expected return calculation assumes simple interest. If loans use compound interest or have different payment schedules, this might not be accurate.

### Issue 2: Time Factor
Expected returns don't account for:
- How long the investment has been active
- Remaining time until maturity
- Partial payments already made

### Issue 3: Risk Not Accounted For
Expected returns assume all open investments will be fully repaid, which may not be true for defaulted loans.

## Recommended Improvements

1. **Time-weighted Returns**: Calculate expected returns based on remaining time
2. **Status-based Calculation**: Exclude defaulted loans from expected returns
3. **Partial Returns**: Account for partial payments already received
4. **ROI Percentage**: Add ROI calculation: `(Actual Returns + Expected Returns) / Total Invested × 100`

## Code Location

The calculation is in: `loans/views.py` → `PortfolioValue` class (lines 604-644)

