📘 EVITO AI - Complete Documentation

⚠️ Current state note (Dec 2025)
- This file captures the original vision. Some filenames/features here don’t exist in the repo as-is.
- For what’s actually implemented now, see:
  - docs/STATE_MAP.md (one-page current flow, real vs placeholder, ports, services)
  - services/streamlit_app/README_streamlit.md (how the current Streamlit AI Debate/queue works)

Key mismatches vs. reality:
- Files like `risk_bot_api_test.py`, `slack_socket_files.py`, `streamlit_dashboard/dashboard.py`, `start_evito.sh` are not present.
- Slack bot is currently a dummy snapshot (no file upload/modals/portfolio flow).
- Streamlit app is the new AI Debate UI (with mocks/queue/library), not the multi-page dashboard described here.
- Risk API exists (`services/risk_bot_api/evito_api_server.py`, default 8081); compose maps risk-service to 8080—align if containerized.
🎯 Table of Contents

    System Overview
    Architecture
    Quick Start Guide
    Slack Integration
    Streamlit Dashboard
    API Documentation
    Workflows & Features
    Deployment
    Troubleshooting

🎯 System Overview

EVITO AI is a professional risk intelligence platform that provides real-time market risk analysis through multiple channels: Slack, Email, and Web Dashboard.
Key Features:

    ⚡ Real-time risk analysis for stocks and portfolios
    💬 Slack bot with interactive commands
    📧 Email bot with automated responses
    📊 Professional Streamlit dashboard
    📄 Portfolio CSV upload & analysis
    🔔 Automated alerts & notifications
    📈 Historical trend analysis

🏗️ Architecture
System Components Flow:
javascript

┌─────────────────────────────────────────────────────────────────┐
│                         EVITO AI SYSTEM                          │
└─────────────────────────────────────────────────────────────────┘
                    ┌──────────────────────┐
                    │   Risk Analysis API  │
                    │   Flask (Port 8081)  │
                    │                      │
                    │  • /analyze          │
                    │  • /health           │
                    │  • /info             │
                    └──────────┬───────────┘
                               │
                               │ HTTP Requests
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌──────────────────┐   ┌─────────────────┐
│  Slack Bot    │    │   Email Bot      │   │   Streamlit     │
│  Socket Mode  │    │   IMAP/SMTP      │   │   Dashboard     │
│               │    │                  │   │   (Port 8501)   │
│  • /risk      │    │  • Monitor inbox │   │                 │
│  • File upload│    │  • Parse tickers │   │  • Live Monitor │
│  • /portfolio │    │  • Send HTML     │   │  • Risk Analyzer│
│  • Buttons    │    │                  │   │  • CSV Upload   │
└───────┬───────┘    └────────┬─────────┘   └────────┬────────┘
        │                     │                       │
        │                     │                       │
        ▼                     ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                         END USERS                            │
│                                                               │
│  👥 Team Members      📧 Email Clients      🌐 Web Users     │
└─────────────────────────────────────────────────────────────┘

Data Flow:
javascript

USER REQUEST
    │
    ├── Via Slack: /risk TSLA
    │       │
    │       ├─→ Slack Bot receives command
    │       │
    │       ├─→ Calls Risk API: GET /analyze?ticker=TSLA
    │       │
    │       ├─→ API calculates risk score
    │       │
    │       └─→ Returns formatted Slack message with:
    │               • Risk score & level
    │               • Progress bars
    │               • Interactive buttons
    │
    ├── Via Email: Subject "Risk NVDA"
    │       │
    │       ├─→ Email Bot monitors IMAP
    │       │
    │       ├─→ Parses ticker from subject/body
    │       │
    │       ├─→ Calls Risk API
    │       │
    │       └─→ Sends HTML email response
    │
    └── Via Streamlit: Enter ticker in web form
            │
            ├─→ Dashboard sends API request
            │
            ├─→ Displays charts & metrics
            │
            └─→ Shows portfolio analysis

File Structure:
javascript

~/EVITO/
│
├── services/
│   │
│   ├── risk_bot_api/
│   │   ├── risk_bot_api_test.py      # Main API (Port 8081)
│   │   └── requirements.txt
│   │
│   ├── slack_handler/
│   │   ├── slack_socket_files.py     # Interactive Slack Bot
│   │   ├── .env                      # Slack tokens
│   │   └── requirements.txt
│   │
│   ├── email_handler/
│   │   ├── email_risk_bot_test.py    # Email monitoring bot
│   │   ├── .env                      # Gmail credentials
│   │   └── requirements.txt
│   │
│   └── streamlit_dashboard/
│       ├── dashboard.py              # Main Streamlit app
│       └── requirements.txt
│
├── start_evito.sh                    # Tmux startup script
└── README.md                         # This file

🚀 Quick Start Guide
1. Prerequisites:
javascript

# Python 3.8+
python3 --version
# pip
pip3 --version
# Git (optional)
git --version

2. Install Dependencies:
javascript

# Navigate to EVITO directory
cd ~/EVITO
# Install for each service
pip3 install flask requests python-dotenv
pip3 install slack-bolt
pip3 install streamlit plotly pandas
pip3 install imapclient python-dotenv

3. Start All Services (Easy Way):
javascript

cd ~/EVITO
chmod +x start_evito.sh
./start_evito.sh

4. Start Services Manually:

Terminal 1 - Risk API:
javascript

cd ~/EVITO/services/risk_bot_api
python3 risk_bot_api_test.py
# Runs on http://localhost:8081

Terminal 2 - Slack Bot:
javascript

cd ~/EVITO/services/slack_handler
python3 slack_socket_files.py

Terminal 3 - Streamlit Dashboard:
javascript

cd ~/EVITO/services/streamlit_dashboard
streamlit run dashboard.py
# Opens browser at http://localhost:8501

Terminal 4 - Email Bot (Optional):
javascript

cd ~/EVITO/services/email_handler
python3 email_risk_bot_test.py

5. Verify Everything is Running:
javascript

# Check API
curl http://localhost:8081/health
# Check Streamlit
# Browser should open automatically
# Or go to: http://localhost:8501
# Check Slack
# Go to Slack and type: /risk TSLA

💬 Slack Integration
Setup Instructions:
1. Create Slack App:

    Go to https://api.slack.com/apps
    Click "Create New App" → "From scratch"
    Name: EVITO AI
    Choose your workspace

2. Configure OAuth Scopes:

Go to OAuth & Permissions → Add these scopes:
javascript

Bot Token Scopes:
├── app_mentions:read       # Detect @mentions
├── channels:history        # Read channel messages
├── channels:read           # Access channel info
├── chat:write              # Send messages
├── commands                # Slash commands
├── files:read              # Read uploaded files
├── files:write             # Write files
├── groups:history          # Private channel history
├── im:history              # Direct message history
├── im:write                # Send DMs
└── users:read              # Read user info

3. Enable Socket Mode:

    Go to Socket Mode → Enable
    Generate App-Level Token
        Name: evito-socket-token
        Scope: connections:write
        Copy token (starts with xapp-)

4. Create Slash Commands:

Go to Slash Commands → Create these:
Command	Description	Usage Hint
/risk	Analyze stock risk	/risk TSLA
/portfolio	Open portfolio form	/portfolio
/risk-report	Generate full report	/risk-report
5. Configure Environment Variables:
javascript

cd ~/EVITO/services/slack_handler
nano .env

Add:
javascript

SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here

6. Install App to Workspace:

    Go to Install App → Install to Workspace
    Authorize the app
    Copy Bot User OAuth Token (starts with xoxb-)
    Paste into .env file

Slack Commands & Features:
Command: /risk TICKER

Analyze a single stock:
javascript

/risk TSLA

Response:
javascript

┌─────────────────────────────────────┐
│  🎯 Risk Analysis: TSLA              │
├─────────────────────────────────────┤
│  Risk Score    │  72/100             │
│  Risk Level    │  🟠 High            │
│  Period        │  90 days            │
│  Timestamp     │  14:32:15           │
├─────────────────────────────────────┤
│  Volatility    ████████░░  80%      │
│  Trend         ██████░░░░  60%      │
│  Market Cycle  █████████░  90%      │
├─────────────────────────────────────┤
│  [Detailed Analysis] [Set Alert]    │
└─────────────────────────────────────┘

Command: /portfolio

Open interactive form to add portfolio:
javascript

/portfolio

Opens Modal:
javascript

┌──────────────────────────────────┐
│   📊 Add Portfolio               │
├──────────────────────────────────┤
│                                  │
│  Tickers (comma-separated):      │
│  ┌────────────────────────────┐  │
│  │ TSLA, AAPL, NVDA, MSFT    │  │
│  └────────────────────────────┘  │
│                                  │
│  Analysis Period:                │
│  ┌────────────────────────────┐  │
│  │ ▼ 90 days (Quarterly)     │  │
│  └────────────────────────────┘  │
│                                  │
│  [Cancel]          [Analyze]     │
└──────────────────────────────────┘

File Upload Workflow:

1. Upload CSV to Slack channel:
javascript

ticker,quantity
TSLA,100
AAPL,50
NVDA,75

2. Bot detects file:
javascript

📄 Portfolio File Detected
File: `portfolio.csv`
Would you like me to analyze this portfolio?
[📊 Analyze Portfolio]  [❌ Cancel]

3. Click "Analyze Portfolio":
javascript

⚡️ Analyzing Portfolio...
✅ Step 1: Downloading file
✅ Step 2: Parsing tickers (3 found)
⚡ Step 3: Analyzing risk...

4. Results displayed:
javascript

┌─────────────────────────────────────────┐
│  🟡 Portfolio Risk Assessment           │
├─────────────────────────────────────────┤
│  Portfolio Risk │ Medium Risk           │
│  Average Score  │ 58.3/100              │
│  Holdings       │ 3 tickers             │
├─────────────────────────────────────────┤
│  Individual Holdings:                   │
│  • TSLA (100 shares) - 🟠 High (72)    │
│  • AAPL (50 shares) - 🟢 Low (38)      │
│  • NVDA (75 shares) - 🟡 Medium (65)   │
├─────────────────────────────────────────┤
│  [📄 Download Report] [🔔 Set Alerts]  │
└─────────────────────────────────────────┘

Slack Workflow Diagram:
javascript

┌──────────────────────────────────────────────────────────────┐
│                  SLACK INTERACTION FLOW                       │
└──────────────────────────────────────────────────────────────┘
USER ACTION                 BOT RESPONSE              API CALL
─────────────────────────────────────────────────────────────────
1️⃣ /risk TSLA
    │
    ├─→ Receives command
    │       │
    │       ├─→ GET /analyze?ticker=TSLA&days=90
    │       │                               │
    │       │                               ▼
    │       │                    ┌──────────────────┐
    │       │                    │  Calculate Risk  │
    │       │                    │  • Volatility    │
    │       │                    │  • Trend         │
    │       │                    │  • Market Cycle  │
    │       │                    └──────────────────┘
    │       │                               │
    │       │◄──────────────────────────────┘
    │       │   Returns JSON
    │       │
    │       └─→ Formats Slack message
    │               • Header with emoji
    │               • Risk metrics grid
    │               • Progress bars
    │               • Interactive buttons
    │
    └─→ Displays result in Slack
2️⃣ Upload portfolio.csv
    │
    ├─→ Detects file_shared event
    │       │
    │       ├─→ Downloads file
    │       │       │
    │       │       ├─→ Parses CSV
    │       │       │       • Extract tickers
    │       │       │       • Extract quantities
    │       │       │
    │       │       └─→ Shows confirmation message
    │       │               [Analyze] [Cancel]
    │       │
    │       └─→ User clicks [Analyze]
    │               │
    │               ├─→ Loop through tickers:
    │               │       For each ticker:
    │               │       GET /analyze?ticker=X
    │               │
    │               └─→ Aggregate results
    │                       • Calculate avg risk
    │                       • Count risk levels
    │                       • Format table
    │
    └─→ Display portfolio analysis
3️⃣ /portfolio (Modal Form)
    │
    ├─→ Opens modal dialog
    │       │
    │       └─→ User fills form:
    │               • Tickers: TSLA,AAPL,NVDA
    │               • Period: 90 days
    │               [Submit]
    │
    ├─→ Form submitted
    │       │
    │       ├─→ Parse input
    │       │       │
    │       │       └─→ For each ticker:
    │       │               GET /analyze
    │       │
    │       └─→ Display results
    │
    └─→ Show interactive report
4️⃣ Interactive Buttons
    │
    ├─→ [Detailed Analysis] clicked
    │       │
    │       └─→ Show expanded view:
    │               • Historical charts
    │               • Risk breakdown
    │               • AI insights
    │
    ├─→ [Set Alert] clicked
    │       │
    │       └─→ Open alert configuration:
    │               • Threshold: < 40 or > 65
    │               • Notification channel
    │               • Frequency
    │
    └─→ [Download Report] clicked
            │
            └─→ Generate PDF report
                    • Send as file attachment
                    • Or provide download link

📊 Streamlit Dashboard
Features:
1. 🏠 Dashboard (Home)

    System status overview
    Real-time metrics (API status, active monitors, alerts)
    Portfolio performance chart
    Risk level distribution (pie chart)
    Recent activity feed

2. 📈 Risk Analyzer

    Single ticker analysis
    Custom time period selection (7, 30, 90, 180, 365 days)
    Risk score visualization with progress bar
    Risk factor breakdown
    AI-powered insights

3. 📄 Portfolio Upload

    CSV file upload
    Automatic parsing
    Batch analysis of multiple tickers
    Results table with color coding:
        🟢 Green: Risk < 40
        🟡 Yellow: Risk 40-65
        🟠 Orange: Risk > 65
    Download results as CSV

4. 📊 Live Monitor

    Real-time system metrics
    Auto-refreshing activity feed
    Requests per minute
    Average response time
    Active users count

5. ⚙️ Settings

    API configuration
    Notification preferences
    Risk threshold customization

Streamlit User Flow:
javascript

┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT DASHBOARD NAVIGATION                  │
└─────────────────────────────────────────────────────────────┘
LANDING PAGE
    │
    ├─→ 🏠 Dashboard
    │   │
    │   ├─→ View System Status
    │   │       • API Health: ✅ Online / ❌ Offline
    │   │       • Active Monitors: 12
    │   │       • Alerts Today: 7
    │   │
    │   ├─→ Portfolio Performance Chart
    │   │       • Line chart with growth trend
    │   │       • YTD performance
    │   │
    │   ├─→ Risk Breakdown Pie Chart
    │   │       • Low: 15
    │   │       • Medium: 8
    │   │       • High: 3
    │   │       • Critical: 1
    │   │
    │   └─→ Recent Activity Log
    │           • Timestamp + Event description
    │
    ├─→ 📈 Risk Analyzer
    │   │
    │   ├─→ Input Form
    │   │       ┌─────────────────────┐
    │   │       │ Ticker: [TSLA    ]  │
    │   │       │ Period: [90 days▼]  │
    │   │       │ [🔍 Analyze Risk]   │
    │   │       └─────────────────────┘
    │   │
    │   ├─→ API Call: GET /analyze?ticker=TSLA&days=90
    │   │
    │   └─→ Display Results
    │           ┌─────────────────────────────┐
    │           │ Risk Score: 72/100          │
    │           │ Risk Level: 🟠 High         │
    │           │ Analysis Period: 90 days    │
    │           ├─────────────────────────────┤
    │           │ [Progress Bar]  ███████░░░  │
    │           ├─────────────────────────────┤
    │           │ Risk Factors:               │
    │           │  Volatility:  ████████░░ 80%│
    │           │  Trend:       ██████░░░░ 60%│
    │           │  Market:      █████████░ 90%│
    │           ├─────────────────────────────┤
    │           │ 💡 Insights:                │
    │           │  ⚠️ High volatility detected│
    │           │  💡 Consider hedging        │
    │           └─────────────────────────────┘
    │
    ├─→ 📄 Portfolio Upload
    │   │
    │   ├─→ File Upload Widget
    │   │       ┌─────────────────────────┐
    │   │       │ 📎 Drop CSV file here   │
    │   │       │    or click to browse   │
    │   │       └─────────────────────────┘
    │   │
    │   ├─→ Display Uploaded Data
    │   │       ┌──────────────────────┐
    │   │       │ Ticker │ Quantity    │
    │   │       ├──────────────────────┤
    │   │       │ TSLA   │ 100         │
    │   │       │ AAPL   │ 50          │
    │   │       │ NVDA   │ 75          │
    │   │       └──────────────────────┘
    │   │
    │   ├─→ Click [🔍 Analyze Portfolio]
    │   │       │
    │   │       ├─→ Progress Bar: "Analyzing TSLA... (1/3)"
    │   │       ├─→ Progress Bar: "Analyzing AAPL... (2/3)"
    │   │       └─→ Progress Bar: "Analyzing NVDA... (3/3)"
    │   │
    │   └─→ Display Results
    │           ┌──────────────────────────────────────┐
    │           │ Average Risk: 58.3/100               │
    │           │ High Risk Holdings: 1                │
    │           │ Total Holdings: 3                    │
    │           ├──────────────────────────────────────┤
    │           │ Ticker │ Qty │ Risk │ Level          │
    │           ├──────────────────────────────────────┤
    │           │ TSLA   │ 100 │  72  │ 🟠 High       │
    │           │ AAPL   │  50 │  38  │ 🟢 Low        │
    │           │ NVDA   │  75 │  65  │ 🟡 Medium     │
    │           ├──────────────────────────────────────┤
    │           │ [📥 Download Results CSV]            │
    │           └──────────────────────────────────────┘
    │
    ├─→ 📊 Live Monitor
    │   │
    │   └─→ Auto-refreshing (every 2s)
    │           ┌──────────────────────────┐
    │           │ Requests/min:    45      │
    │           │ Avg Response:    120ms   │
    │           │ Active Users:    12      │
    │           │ Refresh Count:   156     │
    │           ├──────────────────────────┤
    │           │ 🔔 Recent Events:        │
    │           │ 14:32:15 - Risk analysis │
    │           │ 14:32:18 - Email sent    │
    │           │ 14:32:20 - Slack notify  │
    │           └──────────────────────────┘
    │
    └─→ ⚙️ Settings
        │
        └─→ Configuration Form
                ┌─────────────────────────────┐
                │ API URL: [localhost:8081 ]  │
                │ Timeout: [━━━━━●━━━━] 10s   │
                ├─────────────────────────────┤
                │ ☑ Enable Email Notifications│
                │ ☑ Enable Slack Notifications│
                ├─────────────────────────────┤
                │ Low Risk:    [━━●━━━━━] 40  │
                │ Medium Risk: [━━━━●━━━] 65  │
                ├─────────────────────────────┤
                │ [💾 Save Settings]          │
                └─────────────────────────────┘

Streamlit Code Structure:
javascript

# Page routing
page = st.sidebar.radio("Navigation", [
    "🏠 Dashboard",
    "📈 Risk Analyzer",
    "📄 Portfolio Upload",
    "📊 Live Monitor",
    "⚙️ Settings"
])
# Example: Risk Analyzer page
if page == "📈 Risk Analyzer":
    ticker = st.text_input("Ticker Symbol", "TSLA")
    days = st.selectbox("Period", [7, 30, 90, 180, 365])
    if st.button("🔍 Analyze"):
        # Call API
        response = requests.get(
            f"http://localhost:8081/analyze",
            params={"ticker": ticker, "days": days}
        )
        if response.status_code == 200:
            data = response.json()
            # Display metrics
            st.metric("Risk Score", f"{data['risk_score']}/100")
            st.progress(data['risk_score'] / 100)
            # Show chart
            fig = go.Figure(...)
            st.plotly_chart(fig)

🔌 API Documentation
Base URL: http://localhost:8081
Endpoints:
1. GET /health

Check API status Request:
javascript

curl http://localhost:8081/health

Response:
javascript

{
  "status": "healthy",
  "timestamp": "2024-12-04T14:32:15.123Z"
}

2. GET /analyze

Analyze risk for a ticker Parameters:

    ticker (required): Stock symbol (e.g., TSLA)
    days (optional): Analysis period (default: 90) Request:

javascript

curl "http://localhost:8081/analyze?ticker=TSLA&days=90"

Response:
javascript

{
  "ticker": "TSLA",
  "risk_score": 72,
  "risk_level": "High",
  "analysis_period_days": 90,
  "timestamp": "2024-12-04T14:32:15.123Z",
  "factors": {
    "volatility": 80,
    "trend": 60,
    "market_cycle": 90
  },
  "insights": [
    "High volatility detected in recent trading",
    "Consider hedging strategies for risk mitigation"
  ]
}

3. GET /info

Get API information Request:
javascript

curl http://localhost:8081/info

Response:
javascript

{
  "name": "EVITO Risk Analysis API",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "endpoints": [
    "/health",
    "/analyze",
    "/info"
  ]
}

Risk Score Calculation:
javascript

Risk Score (0-100) = Hash-based mock calculation
│
├─→ < 40:  🟢 Low Risk
├─→ 40-65: 🟡 Medium Risk
├─→ 65-85: 🟠 High Risk
└─→ > 85:  🔴 Critical Risk
Note: Current implementation uses deterministic hash-based
scoring for demonstration. Replace with real market data
API (Alpha Vantage, Yahoo Finance, etc.) in production.

🎬 Workflows & Features
Complete User Journey:
javascript

┌──────────────────────────────────────────────────────────────┐
│              COMPLETE EVITO AI USER JOURNEY                   │
└──────────────────────────────────────────────────────────────┘
SCENARIO 1: Quick Ticker Check
─────────────────────────────────────────────────────────────────
User opens Slack
    │
    ├─→ Types: /risk TSLA
    │       │
    │       └─→ Bot responds in 2 seconds:
    │               ┌───────────────────────┐
    │               │ 🟠 TSLA: 72/100 High │
    │               │ [Details] [Alert]    │
    │               └───────────────────────┘
    │
    └─→ User clicks [Details]
            │
            └─→ Shows expanded analysis with charts
SCENARIO 2: Portfolio Analysis via CSV
─────────────────────────────────────────────────────────────────
User has portfolio.csv on desktop
    │
    ├─→ Drags file into Slack channel
    │       │
    │       └─→ Bot detects: "📄 Portfolio file detected"
    │               [Analyze Portfolio] [Cancel]
    │
    ├─→ User clicks [Analyze Portfolio]
    │       │
    │       ├─→ Bot: "⚡ Analyzing... (1/5)"
    │       ├─→ Bot: "⚡ Analyzing... (2/5)"
    │       └─→ Bot: "✅ Complete!"
    │
    └─→ Results shown with risk distribution
            │
            └─→ User clicks [Download Report]
                    │
                    └─→ PDF sent to email
SCENARIO 3: Email Request
─────────────────────────────────────────────────────────────────
Client sends email: "Risk analysis for NVDA please"
    │
    ├─→ Email bot polls IMAP (every 30s)
    │       │
    │       └─→ Detects new email
    │               │
    │               ├─→ Parses: "NVDA" from body
    │               │
    │               ├─→ Calls API: /analyze?ticker=NVDA
    │               │
    │               └─→ Generates HTML email response:
    │                       ┌──────────────────────┐
    │                       │ NVDA Risk Analysis   │
    │                       │ Score: 65/100        │
    │                       │ Level: 🟡 Medium     │
    │                       │ [View Full Report]   │
    │                       └──────────────────────┘
    │
    └─→ Client receives beautiful email in 1 minute
SCENARIO 4: Web Dashboard Deep Dive
─────────────────────────────────────────────────────────────────
Analyst opens Streamlit dashboard
    │
    ├─→ Sees live system status on homepage
    │       • API: ✅ Online
    │       • Active monitors: 12
    │       • Alerts today: 7
    │
    ├─→ Clicks "📈 Risk Analyzer"
    │       │
    │       ├─→ Enters: TSLA, 180 days
    │       │
    │       └─→ Detailed analysis loads:
    │               • Risk score with progress bar
    │               • Factor breakdown (volatility, trend, cycle)
    │               • AI insights
    │               • Historical chart
    │
    ├─→ Clicks "📄 Portfolio Upload"
    │       │
    │       ├─→ Uploads portfolio.csv (25 tickers)
    │       │
    │       └─→ Batch analysis runs:
    │               ⏳ Progress: 25/25 complete
    │               ✅ Average risk: 58/100
    │               📊 Results table (color-coded)
    │               📥 Download button
    │
    └─→ Clicks "📊 Live Monitor"
            │
            └─→ Real
