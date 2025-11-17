# Investor Charts API - Quick Reference

## API Endpoints

### 1. Investment Performance Chart
```
GET /api/investor/charts/performance/
```

**Query Parameters:**
- `period` (optional): Number of periods (default: 12)
- `period_type` (optional): `month`, `quarter`, or `year` (default: `month`)

**Returns:** Line, bar, area, and transaction trend chart data

### 2. Portfolio Distribution Chart
```
GET /api/investor/charts/distribution/
```

**Query Parameters:** None

**Returns:** Pie/donut chart data for loan status, loan purpose, and investment status distributions

---

## Quick Integration Examples

### React with Chart.js

```jsx
import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';

function PerformanceChart() {
  const [chartData, setChartData] = useState(null);
  
  useEffect(() => {
    fetch('/api/investor/charts/performance/?period=12', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    .then(res => res.json())
    .then(data => {
      if (data.code === 1) {
        setChartData(data.data.charts.line_chart);
      }
    });
  }, []);
  
  if (!chartData) return <div>Loading...</div>;
  
  return <Line data={chartData} options={{ responsive: true }} />;
}
```

### React with Recharts

```jsx
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

function DistributionChart() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('/api/investor/charts/distribution/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    .then(res => res.json())
    .then(result => {
      if (result.code === 1) {
        const chartData = result.data.loan_status_distribution.chart_data;
        const transformed = chartData.labels.map((label, i) => ({
          name: label,
          value: chartData.datasets[0].data[i]
        }));
        setData({ data: transformed, colors: chartData.datasets[0].backgroundColor });
      }
    });
  }, []);
  
  if (!data) return <div>Loading...</div>;
  
  return (
    <PieChart width={400} height={400}>
      <Pie data={data.data} dataKey="value" nameKey="name">
        {data.data.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={data.colors[index]} />
        ))}
      </Pie>
      <Tooltip />
      <Legend />
    </PieChart>
  );
}
```

---

## Response Structure Summary

### Performance Chart Response
```json
{
  "code": 1,
  "message": "...",
  "data": {
    "charts": {
      "line_chart": { "labels": [...], "datasets": [...] },
      "bar_chart": { "labels": [...], "datasets": [...] },
      "area_chart": { "labels": [...], "datasets": [...] },
      "transaction_trends": { "labels": [...], "datasets": [...] }
    },
    "summary": {
      "total_invested": 15000.00,
      "total_returns": 750.00,
      "roi_percentage": 5.00,
      "current_portfolio_value": 15750.00
    }
  }
}
```

### Distribution Chart Response
```json
{
  "code": 1,
  "message": "...",
  "data": {
    "loan_status_distribution": {
      "chart_data": { "labels": [...], "datasets": [...] },
      "summary": { "breakdown": {...} }
    },
    "loan_purpose_distribution": {
      "chart_data": { "labels": [...], "datasets": [...] },
      "summary": { "breakdown": {...} }
    },
    "investment_status_distribution": {
      "chart_data": { "labels": [...], "datasets": [...] }
    },
    "roi_by_status": {...}
  }
}
```

---

## Important Notes

1. **Authentication**: Both APIs require Bearer token authentication
2. **Role**: User must have "Investor" role
3. **Data Format**: All chart data is in Chart.js compatible format
4. **Empty States**: APIs return empty arrays if no data exists
5. **Real-time**: Data is calculated from database in real-time

---

## Common Use Cases

### Display Portfolio Summary
Use `summary` object from performance chart API:
- Total invested
- Total returns
- ROI percentage
- Current portfolio value

### Show Investment Trends
Use `line_chart` or `area_chart` from performance chart API:
- Monthly investment trends
- Returns over time
- Cumulative portfolio growth

### Visualize Portfolio Distribution
Use distribution chart API:
- Loan status breakdown (pie chart)
- Loan purpose breakdown (pie chart)
- Investment status (open vs closed)

### Display ROI by Status
Use `roi_by_status` from distribution chart API:
- Table or cards showing ROI for each loan status
- Helps identify best performing investment categories

---

## Error Handling

Always check `code` field in response:
- `code: 1` = Success
- `code: 0` = Error

Example:
```javascript
const response = await fetch('/api/investor/charts/performance/');
const result = await response.json();

if (result.code === 1) {
  // Success - use result.data
} else {
  // Error - show result.message
  console.error(result.message);
}
```

