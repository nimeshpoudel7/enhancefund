# Investor Charts & Graphs API Documentation

## Overview
This document describes the two chart/graph APIs created for the investor frontend. Both APIs provide real-time data from the database and are designed to work with popular charting libraries like Chart.js, Recharts, or any other charting library that accepts standard data formats.

---

## API 1: Investment Performance Chart API

### Endpoint
```
GET /api/investor/charts/performance/
```

### Description
Returns comprehensive performance data for line charts, bar charts, and area charts showing investment performance over time, returns, cumulative values, and transaction trends.

### Authentication
- **Required**: Yes
- **Role**: Investor only
- **Header**: `Authorization: Bearer <token>`

### Query Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `period` | integer | No | `12` | Number of periods to retrieve data for |
| `period_type` | string | No | `month` | Type of period: `month`, `quarter`, or `year` |

### Example Requests

#### Get last 12 months of data (default)
```http
GET /api/investor/charts/performance/
Authorization: Bearer <token>
```

#### Get last 6 months of data
```http
GET /api/investor/charts/performance/?period=6&period_type=month
Authorization: Bearer <token>
```

#### Get last 2 quarters of data
```http
GET /api/investor/charts/performance/?period=2&period_type=quarter
Authorization: Bearer <token>
```

#### Get last 3 years of data
```http
GET /api/investor/charts/performance/?period=3&period_type=year
Authorization: Bearer <token>
```

### Response Structure

#### Success Response (200 OK)
```json
{
  "code": 1,
  "message": "Investment performance chart data retrieved successfully",
  "data": {
    "charts": {
      "line_chart": {
        "labels": ["2024-01", "2024-02", "2024-03", ...],
        "datasets": [
          {
            "label": "Total Invested",
            "data": [1000.00, 2500.00, 3500.00, ...],
            "borderColor": "rgb(75, 192, 192)",
            "backgroundColor": "rgba(75, 192, 192, 0.2)",
            "tension": 0.1
          },
          {
            "label": "Total Returns",
            "data": [50.00, 125.00, 175.00, ...],
            "borderColor": "rgb(255, 99, 132)",
            "backgroundColor": "rgba(255, 99, 132, 0.2)",
            "tension": 0.1
          },
          {
            "label": "Cumulative Value",
            "data": [1050.00, 2625.00, 3675.00, ...],
            "borderColor": "rgb(54, 162, 235)",
            "backgroundColor": "rgba(54, 162, 235, 0.2)",
            "tension": 0.1
          }
        ]
      },
      "bar_chart": {
        "labels": ["2024-01", "2024-02", "2024-03", ...],
        "datasets": [
          {
            "label": "Investments",
            "data": [1000.00, 1500.00, 1000.00, ...],
            "backgroundColor": "rgba(75, 192, 192, 0.6)"
          },
          {
            "label": "Returns",
            "data": [50.00, 75.00, 50.00, ...],
            "backgroundColor": "rgba(255, 99, 132, 0.6)"
          }
        ]
      },
      "area_chart": {
        "labels": ["2024-01", "2024-02", "2024-03", ...],
        "datasets": [
          {
            "label": "Cumulative Investment",
            "data": [1050.00, 2625.00, 3675.00, ...],
            "backgroundColor": "rgba(75, 192, 192, 0.3)",
            "borderColor": "rgb(75, 192, 192)",
            "fill": true
          }
        ]
      },
      "transaction_trends": {
        "labels": ["2024-01", "2024-02", "2024-03", ...],
        "datasets": [
          {
            "label": "Deposit",
            "data": [5000.00, 3000.00, 2000.00, ...],
            "backgroundColor": "rgba(75, 192, 192, 0.6)"
          },
          {
            "label": "Withdrawal",
            "data": [500.00, 200.00, 100.00, ...],
            "backgroundColor": "rgba(255, 99, 132, 0.6)"
          },
          {
            "label": "Investment",
            "data": [1000.00, 1500.00, 1000.00, ...],
            "backgroundColor": "rgba(54, 162, 235, 0.6)"
          },
          {
            "label": "Payment",
            "data": [0.00, 0.00, 0.00, ...],
            "backgroundColor": "rgba(255, 206, 86, 0.6)"
          }
        ]
      }
    },
    "summary": {
      "total_invested": 15000.00,
      "total_returns": 750.00,
      "total_investments": 15,
      "roi_percentage": 5.00,
      "period": "12 month(s)",
      "current_portfolio_value": 15750.00
    },
    "period": {
      "start_date": "2023-01-01T00:00:00Z",
      "end_date": "2024-01-01T00:00:00Z",
      "type": "month"
    }
  }
}
```

#### Error Response (500 Internal Server Error)
```json
{
  "code": 0,
  "message": "Error retrieving chart data: <error message>",
  "data": {}
}
```

### Chart Data Format
The API returns data in a format compatible with Chart.js. Each chart type includes:
- **labels**: Array of month labels (YYYY-MM format)
- **datasets**: Array of dataset objects with data points and styling

### Use Cases
1. **Line Chart**: Display investment performance trends over time
2. **Bar Chart**: Compare monthly investments vs returns
3. **Area Chart**: Show cumulative portfolio growth
4. **Transaction Trends**: Multi-line chart showing different transaction types

---

## API 2: Portfolio Distribution Chart API

### Endpoint
```
GET /api/investor/charts/distribution/
```

### Description
Returns portfolio distribution data for pie charts and donut charts showing how investments are distributed across loan statuses, loan purposes, and investment statuses.

### Authentication
- **Required**: Yes
- **Role**: Investor only
- **Header**: `Authorization: Bearer <token>`

### Query Parameters
None

### Example Request
```http
GET /api/investor/charts/distribution/
Authorization: Bearer <token>
```

### Response Structure

#### Success Response (200 OK)
```json
{
  "code": 1,
  "message": "Portfolio distribution chart data retrieved successfully",
  "data": {
    "loan_status_distribution": {
      "chart_data": {
        "labels": ["Pending", "Processing", "Approved", "Repaid", "Defaulted"],
        "datasets": [
          {
            "data": [2000.00, 3000.00, 5000.00, 4000.00, 1000.00],
            "backgroundColor": [
              "#FF6384",
              "#36A2EB",
              "#4BC0C0",
              "#9966FF",
              "#FF9F40"
            ],
            "borderColor": "#ffffff",
            "borderWidth": 2
          }
        ]
      },
      "summary": {
        "total_amount": 15000.00,
        "breakdown": {
          "pending": {
            "amount": 2000.00,
            "count": 2,
            "percentage": 13.33
          },
          "processing": {
            "amount": 3000.00,
            "count": 3,
            "percentage": 20.00
          },
          "approved": {
            "amount": 5000.00,
            "count": 5,
            "percentage": 33.33
          },
          "repaid": {
            "amount": 4000.00,
            "count": 4,
            "percentage": 26.67
          },
          "defaulted": {
            "amount": 1000.00,
            "count": 1,
            "percentage": 6.67
          }
        }
      }
    },
    "loan_purpose_distribution": {
      "chart_data": {
        "labels": [
          "Home Improvement",
          "Business Expansion",
          "Debt Consolidation",
          "Education",
          "Medical Expenses"
        ],
        "datasets": [
          {
            "data": [5000.00, 4000.00, 3000.00, 2000.00, 1000.00],
            "backgroundColor": [
              "#FF6384",
              "#36A2EB",
              "#4BC0C0",
              "#9966FF",
              "#FF9F40"
            ],
            "borderColor": "#ffffff",
            "borderWidth": 2
          }
        ]
      },
      "summary": {
        "total_purposes": 5,
        "breakdown": {
          "Home Improvement": {
            "amount": 5000.00,
            "count": 5,
            "percentage": 33.33
          },
          "Business Expansion": {
            "amount": 4000.00,
            "count": 4,
            "percentage": 26.67
          },
          "Debt Consolidation": {
            "amount": 3000.00,
            "count": 3,
            "percentage": 20.00
          },
          "Education": {
            "amount": 2000.00,
            "count": 2,
            "percentage": 13.33
          },
          "Medical Expenses": {
            "amount": 1000.00,
            "count": 1,
            "percentage": 6.67
          }
        }
      }
    },
    "investment_status_distribution": {
      "chart_data": {
        "labels": ["Open", "closed"],
        "datasets": [
          {
            "data": [10000.00, 5000.00],
            "backgroundColor": [
              "#36A2EB",
              "#4BC0C0"
            ],
            "borderColor": "#ffffff",
            "borderWidth": 2
          }
        ]
      },
      "summary": {
        "breakdown": {
          "Open": {
            "amount": 10000.00,
            "count": 10,
            "percentage": 66.67
          },
          "closed": {
            "amount": 5000.00,
            "count": 5,
            "percentage": 33.33
          }
        }
      }
    },
    "roi_by_status": {
      "pending": {
        "invested": 2000.00,
        "returns": 0.00,
        "roi_percentage": 0.00
      },
      "processing": {
        "invested": 3000.00,
        "returns": 0.00,
        "roi_percentage": 0.00
      },
      "approved": {
        "invested": 5000.00,
        "returns": 250.00,
        "roi_percentage": 5.00
      },
      "repaid": {
        "invested": 4000.00,
        "returns": 400.00,
        "roi_percentage": 10.00
      },
      "defaulted": {
        "invested": 1000.00,
        "returns": 0.00,
        "roi_percentage": 0.00
      }
    },
    "total_investments": 15,
    "total_invested_amount": 15000.00
  }
}
```

#### Error Response (500 Internal Server Error)
```json
{
  "code": 0,
  "message": "Error retrieving distribution chart data: <error message>",
  "data": {}
}
```

### Chart Data Format
The API returns data in Chart.js pie/donut chart format:
- **labels**: Array of category labels
- **datasets**: Single dataset with:
  - **data**: Array of values
  - **backgroundColor**: Array of colors matching the data
  - **borderColor**: Border color for slices
  - **borderWidth**: Width of borders

### Use Cases
1. **Loan Status Distribution**: Pie chart showing portfolio distribution by loan status
2. **Loan Purpose Distribution**: Pie/donut chart showing top 10 loan purposes
3. **Investment Status Distribution**: Pie chart showing open vs closed investments
4. **ROI Analysis**: Table/card display showing ROI by loan status

---

## Data Sources

Both APIs query real-time data from the following database tables:
- `investment` - Investment records
- `loan` - Loan information
- `transaction` - Transaction history
- `loan_repayment_schedule` - Repayment schedules

### Real-time Calculations
- **Investment amounts**: Summed from actual investment records
- **Returns**: Calculated from `net_return` field in investments
- **ROI**: Calculated as (returns / invested) * 100
- **Cumulative values**: Running totals calculated from historical data
- **Monthly aggregations**: Grouped by month using Django's `TruncMonth`

---

## Frontend Integration Examples

### Chart.js Integration

#### Line Chart (Performance)
```javascript
// Fetch data
const response = await fetch('/api/investor/charts/performance/?period=12', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const { data } = await response.json();

// Create line chart
const ctx = document.getElementById('performanceChart').getContext('2d');
new Chart(ctx, {
  type: 'line',
  data: data.charts.line_chart,
  options: {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }
});
```

#### Pie Chart (Distribution)
```javascript
// Fetch data
const response = await fetch('/api/investor/charts/distribution/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const { data } = await response.json();

// Create pie chart for loan status
const ctx = document.getElementById('statusChart').getContext('2d');
new Chart(ctx, {
  type: 'pie',
  data: data.loan_status_distribution.chart_data,
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'right'
      }
    }
  }
});
```

### Recharts Integration

#### Line Chart (Performance)
```jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

// Fetch and transform data
const response = await fetch('/api/investor/charts/performance/?period=12', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data } = await response.json();

// Transform for Recharts
const chartData = data.charts.line_chart.labels.map((label, index) => ({
  month: label,
  invested: data.charts.line_chart.datasets[0].data[index],
  returns: data.charts.line_chart.datasets[1].data[index],
  cumulative: data.charts.line_chart.datasets[2].data[index]
}));

// Render chart
<LineChart width={800} height={400} data={chartData}>
  <CartesianGrid strokeDasharray="3 3" />
  <XAxis dataKey="month" />
  <YAxis />
  <Tooltip />
  <Legend />
  <Line type="monotone" dataKey="invested" stroke="#4BC0C0" />
  <Line type="monotone" dataKey="returns" stroke="#FF6384" />
  <Line type="monotone" dataKey="cumulative" stroke="#36A2EB" />
</LineChart>
```

#### Pie Chart (Distribution)
```jsx
import { PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';

// Fetch data
const response = await fetch('/api/investor/charts/distribution/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data } = await response.json();

// Transform for Recharts
const pieData = data.loan_status_distribution.chart_data.labels.map((label, index) => ({
  name: label,
  value: data.loan_status_distribution.chart_data.datasets[0].data[index]
}));

// Render chart
<PieChart width={400} height={400}>
  <Pie
    data={pieData}
    cx={200}
    cy={200}
    labelLine={false}
    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
    outerRadius={80}
    fill="#8884d8"
    dataKey="value"
  >
    {pieData.map((entry, index) => (
      <Cell key={`cell-${index}`} fill={data.loan_status_distribution.chart_data.datasets[0].backgroundColor[index]} />
    ))}
  </Pie>
  <Tooltip />
  <Legend />
</PieChart>
```

---

## Error Handling

### Common Error Scenarios

1. **Unauthorized (401)**: User not authenticated or not an investor
   ```json
   {
     "code": 0,
     "message": "Authentication credentials were not provided.",
     "data": {}
   }
   ```

2. **No Data Available**: User has no investments
   - APIs will return empty arrays and zero values
   - Charts will render with empty states

3. **Server Error (500)**: Database or calculation error
   - Check server logs for detailed error messages
   - Error message included in response

---

## Performance Considerations

- **Database Queries**: Optimized with `select_related()` and `prefetch_related()`
- **Aggregations**: Performed at database level using Django ORM aggregations
- **Caching**: Consider implementing caching for frequently accessed data
- **Pagination**: Not required as data is aggregated by month/period

---

## Testing

### Manual Testing
1. Ensure user is authenticated as an investor
2. Create some test investments with different statuses and purposes
3. Call both APIs and verify data structure
4. Test with different period parameters

### Example cURL Commands
```bash
# Performance Chart
curl -X GET "http://localhost:8000/api/investor/charts/performance/?period=6" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Distribution Chart
curl -X GET "http://localhost:8000/api/investor/charts/distribution/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Notes

- All monetary values are in CAD (Canadian Dollars)
- Dates are returned in ISO 8601 format
- Percentages are rounded to 2 decimal places
- Amounts are rounded to 2 decimal places
- Loan purpose distribution shows top 10 purposes only
- Empty months are not included in the response (only months with data)

---

## Support

For issues or questions:
1. Check server logs for detailed error messages
2. Verify user has investor role
3. Ensure database has investment data
4. Check authentication token validity

