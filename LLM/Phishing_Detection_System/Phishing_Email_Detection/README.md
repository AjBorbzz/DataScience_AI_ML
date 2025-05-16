# Phishing Email Analysis Dashboard

![Dashboard Screenshot]()

## Overview

The Phishing Email Analysis Dashboard is an interactive Streamlit application that visualizes email security analysis results. This tool transforms raw security analysis data into an intuitive, information-rich dashboard that helps security professionals and end-users quickly understand potential email threats.

## Features

- **Comprehensive Threat Assessment**: Clear verdict and confidence score presentation
- **Multi-faceted Analysis**: Examines email headers, content, authentication mechanisms, and domains
- **Visual Risk Indicators**: Color-coded risk levels and interactive components
- **Detailed IOC Analysis**: Breakdown of Indicators of Compromise with context 
- **Actionable Recommendations**: Clear guidance on next steps based on analysis results

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package installer)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/phishing-dashboard.git
   cd phishing-dashboard
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Dashboard

Launch the Streamlit application:

```bash
streamlit run phishing_dashboard.py
```

The dashboard will open in your default web browser at `http://localhost:8501`.

### Analyzing Custom Data

To analyze your own email data instead of the provided sample:

1. Modify the `sample_output` variable in the code with your analysis output
2. Update the extracted data variables (`email_data`, `auth_results`, etc.)
3. Restart the application to see your custom data

### Dashboard Sections

#### 1. Email Summary
Provides a quick overview of the analyzed email including subject, sender, authentication status, and suspicious URLs.

#### 2. Detailed Analysis
Divided into three tabs:
- **Reasoning**: Explains why the email is classified as a threat
- **Technical Indicators**: Shows authentication results and specific risk indicators
- **IOCs**: Lists all identified Indicators of Compromise

#### 3. Threat Assessment
Visual representation of the overall verdict and confidence score, along with a breakdown of risk scores by category.

#### 4. Recommendations
Actionable steps users should take in response to the identified threat.

## Customization

### Styling

The dashboard uses custom CSS for styling. Modify the CSS section at the beginning of the script to customize the appearance:

```python
st.markdown("""
<style>
    .header-container {
        background-color: #1E3A8A;
        padding: 1.5rem;
        border-radius: 0.5rem;
        /* Add or modify styles here */
    }
    /* Other style classes */
</style>
""", unsafe_allow_html=True)
```

### Adding New Features

#### Additional Analysis Metrics
Add new metrics by creating additional data structures and visualization components:

```python
new_metrics = {
    "Metric1": "Value1",
    "Metric2": "Value2"
}

st.markdown("### New Metrics Section")
for key, value in new_metrics.items():
    st.markdown(f"**{key}:** {value}")
```

#### Custom Charts
Add new visualizations using Streamlit's charting capabilities:

```python
import altair as alt
# Create chart data
chart_data = pd.DataFrame({
    "Category": ["A", "B", "C"],
    "Values": [10, 20, 30]
})
# Create and display chart
chart = alt.Chart(chart_data).mark_bar().encode(x="Category", y="Values")
st.altair_chart(chart, use_container_width=True)
```

## Integration Options

### API Integration

To connect this dashboard to live email analysis systems:

1. Create a function to call your analysis API:
   ```python
   def get_analysis_from_api(email_id):
       # API call code here
       return analysis_data
   ```

2. Use the returned data to populate the dashboard variables.

### Database Integration

To retrieve analysis results from a database:

1. Set up a database connection:
   ```python
   import sqlite3
   conn = sqlite3.connect("your_database.db")
   ```

2. Query and use the data:
   ```python
   query = "SELECT * FROM email_analysis WHERE id = ?"
   result = conn.execute(query, (email_id,)).fetchone()
   ```

## Security Considerations

- This dashboard is designed for visualization only and does not perform the actual email analysis
- Ensure the application is deployed in a secure environment if displaying sensitive information
- Consider implementing authentication if deployed in a multi-user environment

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Streamlit for the amazing framework
- [Placeholder] for inspiration on the security analysis methodology

---

## Example Analysis Output

The dashboard is pre-configured to visualize the following sample analysis:

```
I'll analyze this email carefully using the structured threat detection approach.

## Analysis

### Email Data Assessment
- **Subject**: "Urgent: Your Account Has Been Locked!" uses urgency tactics common in phishing
- **Sender**: Claims to be Chase Bank but uses a suspicious domain (chase-verification.com)
- **Authentication**: All email authentication mechanisms failed (SPF, DKIM, DMARC)
- **Content**: Brief message with urgent call to action and suspicious link
- **URL**: Domain "chase-verification-login.com" is not an official Chase Bank domain

[...remainder of sample analysis...]
```

This sample demonstrates how the dashboard transforms raw analysis text into an interactive visualization.
