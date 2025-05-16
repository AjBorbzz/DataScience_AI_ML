import streamlit as st
import pandas as pd
import re

# Set page configuration
st.set_page_config(
    page_title="Email Threat Analysis",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .header-container {
        background-color: #1E3A8A;
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-label {
        font-size: 1rem;
        color: #555;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
    }
    .highlight {
        background-color: #FFE2E2;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-weight: bold;
    }
    .security-passed {
        color: #10B981;
        font-weight: bold;
    }
    .security-failed {
        color: #EF4444;
        font-weight: bold;
    }
    .indicator-high {
        color: #EF4444;
        font-weight: bold;
    }
    .indicator-medium {
        color: #F59E0B;
        font-weight: bold;
    }
    .indicator-low {
        color: #10B981;
        font-weight: bold;
    }
    .sidebar-content {
        padding: 1rem;
    }
    .info-box {
        background-color: #E0F2FE;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sample phishing analysis output
sample_output = """
I'll analyze this email carefully using the structured threat detection approach.

## Analysis

### Email Data Assessment
- **Subject**: "Urgent: Your Account Has Been Locked!" uses urgency tactics common in phishing
- **Sender**: Claims to be Chase Bank but uses a suspicious domain (chase-verification.com)
- **Authentication**: All email authentication mechanisms failed (SPF, DKIM, DMARC)
- **Content**: Brief message with urgent call to action and suspicious link
- **URL**: Domain "chase-verification-login.com" is not an official Chase Bank domain

### IOC Enrichment
- **Domain analysis**: "chase-verification.com" 
   - Not a legitimate Chase domain (legitimate would be chase.com)
   - Uses hyphenated domain naming pattern common in phishing
- **URL analysis**: "http://chase-verification-login.com"
   - Uses HTTP instead of HTTPS (lacks encryption)
   - Domain mimics Chase Bank but is not authentic
   - Likely a credential harvesting page

## Output

- **Verdict**: Phishing
- **Confidence**: 95%
- **Reasoning**:
   - Email fails all authentication checks (SPF, DKIM, DMARC)
   - Sender domain "chase-verification.com" is not an official Chase domain
   - Uses classic phishing tactics: urgency, fear, and impersonation of a financial institution
   - Contains suspicious URL that mimics the bank's name but on an unofficial domain
   - Lacks specific customer information that would be in legitimate communications

- **IOC Enrichment**:
   - chase-verification.com: Suspicious domain mimicking Chase Bank, not affiliated with legitimate financial institution
   - chase-verification-login.com: Likely credential harvesting site, not an official Chase domain
   - SPF/DKIM/DMARC failures: Indicates the email is not actually from the claimed sender

This is a clear phishing attempt designed to trick users into believing their Chase account has security issues requiring immediate action, with the goal of stealing login credentials.
"""

# Extract information from the sample output
verdict = "Phishing"
confidence = "95%"

# Parse data for visualization
email_data = {
    "Subject": "Urgent: Your Account Has Been Locked!",
    "Sender": "chase-verification.com (Claiming to be Chase Bank)",
    "Authentication": "Failed (SPF, DKIM, DMARC)",
    "Content": "Brief message with urgent call to action and suspicious link",
    "URL": "http://chase-verification-login.com (Not an official Chase Bank domain)"
}

auth_results = {
    "SPF": "Failed",
    "DKIM": "Failed", 
    "DMARC": "Failed"
}

indicators = [
    {"Name": "Urgency language", "Type": "Social Engineering", "Risk": "High"},
    {"Name": "Suspicious sender domain", "Type": "Impersonation", "Risk": "High"},
    {"Name": "Authentication failures", "Type": "Technical", "Risk": "High"},
    {"Name": "Suspicious URL", "Type": "Technical", "Risk": "High"},
    {"Name": "HTTP instead of HTTPS", "Type": "Technical", "Risk": "Medium"},
    {"Name": "Lack of personal information", "Type": "Content", "Risk": "Medium"}
]

iocs = [
    {"IOC": "chase-verification.com", "Type": "Domain", "Description": "Suspicious domain mimicking Chase Bank"},
    {"IOC": "chase-verification-login.com", "Type": "URL", "Description": "Likely credential harvesting site"},
    {"IOC": "SPF/DKIM/DMARC failures", "Type": "Email Authentication", "Description": "Indicates the email is not from the claimed sender"}
]

reasoning = [
    "Email fails all authentication checks (SPF, DKIM, DMARC)",
    "Sender domain 'chase-verification.com' is not an official Chase domain",
    "Uses classic phishing tactics: urgency, fear, and impersonation of a financial institution",
    "Contains suspicious URL that mimics the bank's name but on an unofficial domain",
    "Lacks specific customer information that would be in legitimate communications"
]

# Display header section
st.markdown("""
<div class="header-container">
    <h1>📧 Email Threat Analysis Dashboard</h1>
    <p>Comprehensive analysis of potentially malicious email content</p>
</div>
""", unsafe_allow_html=True)

# Create a sidebar with additional information
with st.sidebar:
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRlAZjz6VSrH-fVVJxLQlHj0_oLpr0YdXI1qUhxo3HUlw&s", width=100)
    st.markdown("### Threat Analysis Results")
    st.markdown(f"**Verdict:** <span class='indicator-high'>{verdict}</span>", unsafe_allow_html=True)
    st.markdown(f"**Confidence:** {confidence}")
    
    st.markdown("### Quick Actions")
    st.button("Report as False Positive")
    st.button("Block Sender Domain")
    st.button("Export Analysis")
    
    st.markdown("### About")
    st.markdown("""
    This dashboard presents the results of an automated email security analysis.
    It evaluates potential threats by examining email headers, content, and related indicators of compromise.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Create main dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 📌 Email Summary")
    
    # Email data table
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    for key, value in email_data.items():
        if key == "Authentication" and value.startswith("Failed"):
            st.markdown(f"**{key}:** <span class='security-failed'>{value}</span>", unsafe_allow_html=True)
        elif key == "URL" and "Not an official" in value:
            st.markdown(f"**{key}:** <span class='security-failed'>{value}</span>", unsafe_allow_html=True)
        elif key == "Subject" and "Urgent" in value:
            st.markdown(f"**{key}:** <span class='highlight'>{value}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**{key}:** {value}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("## 🔍 Detailed Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Reasoning", "Technical Indicators", "IOCs"])
    
    with tab1:
        st.markdown("### Why this is likely a phishing attempt:")
        for i, reason in enumerate(reasoning, 1):
            st.markdown(f"{i}. {reason}")
            
    with tab2:
        st.markdown("### Authentication Results")
        auth_df = pd.DataFrame({"Check": auth_results.keys(), "Result": auth_results.values()})
        
        # Custom styling for the authentication results
        def color_auth_results(val):
            color = 'red' if val == "Failed" else 'green'
            return f'color: {color}; font-weight: bold'
        
        st.dataframe(auth_df.style.applymap(color_auth_results, subset=['Result']), hide_index=True)
        
        st.markdown("### Risk Indicators")
        indicators_df = pd.DataFrame(indicators)
        
        # Custom styling for the risk indicators
        def color_risk(val):
            if val == "High":
                color = 'red'
            elif val == "Medium":
                color = 'orange'
            else:
                color = 'green'
            return f'color: {color}; font-weight: bold'
        
        st.dataframe(indicators_df.style.applymap(color_risk, subset=['Risk']), hide_index=True)
            
    with tab3:
        st.markdown("### Indicators of Compromise")
        st.dataframe(pd.DataFrame(iocs), hide_index=True)

with col2:
    # Overall threat score visualization
    st.markdown("## 📊 Threat Assessment")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='metric-label'>Verdict</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value indicator-high'>{verdict}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_b:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("<p class='metric-label'>Confidence</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='metric-value'>{confidence}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Risk category breakdown
    st.markdown("### Risk Category Breakdown")
    
    categories = {
        "Social Engineering": 90,
        "Authentication": 100,
        "Domain Legitimacy": 95,
        "Content Analysis": 85
    }
    
    chart_data = pd.DataFrame({
        "Category": categories.keys(),
        "Risk Score": categories.values()
    })
    
    st.bar_chart(chart_data.set_index("Category"), color="#FF4B4B")
    
    # Recommendations section
    st.markdown("## 🛡️ Recommendations")
    
    recommendations = [
        "Do not click on any links in this email",
        "Do not provide any personal information",
        "Report this email as phishing to IT security",
        "If concerned about your account, contact Chase Bank directly through official channels",
        "Block the sender domains in your email security settings"
    ]
    
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")

# Add final note
st.markdown("---")
st.markdown("""
<div class='info-box'>
<strong>Analysis Summary:</strong> This is a clear phishing attempt designed to trick users into believing their Chase account has security issues requiring immediate action, with the goal of stealing login credentials.
</div>
""", unsafe_allow_html=True)

# Add timestamp
st.markdown(f"_Analysis generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}_")