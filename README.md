# PennyWise 💰

A comprehensive personal finance management application with both web frontend and Telegram bot integration. Track income, expenses, and stay within budget limits through intelligent monitoring and visual reporting.

## 🎯 Overview

PennyWise is a full-stack personal finance application that provides both a modern web interface and Telegram bot integration. Upload your transaction data, set budgets for different categories, and get instant insights with beautiful charts and timely alerts when you're approaching your spending limits.

## ✨ Features

### 🌐 Web Application
- **Modern React Frontend**: Built with TypeScript, Tailwind CSS, and comprehensive internationalization
- **Responsive Design**: Mobile-first design that works on all devices
- **RTL Support**: Full support for Persian language with right-to-left layout
- **Dark Mode**: Theme switching capability
- **Real-time Dashboard**: Live financial overview with interactive charts
- **CSV Import/Export**: Drag-and-drop file upload with robust error handling
- **Budget Management**: Visual budget tracking with progress indicators
- **Comprehensive Reports**: Multiple report types with filtering and export

### 📱 Telegram Bot
- **CSV Upload**: Upload transaction files directly through Telegram
- **Quick Commands**: Set budgets and view reports with simple commands
- **Instant Notifications**: Real-time budget alerts and summaries
- **Chart Generation**: Visual reports sent directly to your chat

### 📊 Transaction Management
- **CSV Import**: Upload your bank statements or transaction files in CSV format
- **Automatic Processing**: Smart parsing and categorization of income and expenses
- **Data Validation**: Ensures data integrity and handles various CSV formats
- **Manual Entry**: Add transactions directly through the web interface
- **Duplicate Detection**: Automatic detection and prevention of duplicate transactions

### 📈 Visual Reports & Analytics
- **Interactive Charts**: Generate beautiful visualizations using Chart.js and Recharts
- **Income vs Expense Analysis**: Clear breakdown of your financial flow
- **Category-wise Reports**: Detailed insights into spending by category
- **Time-based Analysis**: Track your financial trends over weeks, months, and years
- **Export Capabilities**: Download charts and reports as images or PDFs

### 🎯 Smart Budget Management
- **Custom Budget Setting**: Define spending limits for each expense category
- **Real-time Monitoring**: Continuous tracking of your spending against budgets
- **Intelligent Alerts**: Get notified when approaching or exceeding budget limits
- **Budget Performance**: Visual indicators of how well you're sticking to your financial goals
- **Multiple Time Periods**: Weekly, monthly, and yearly budget tracking

### 🔔 Notification System
- **Threshold Alerts**: Customizable warnings at 75%, 90%, and 100% of budget
- **Daily/Weekly Summaries**: Regular updates on your financial status
- **Overspend Notifications**: Immediate alerts when budgets are exceeded
- **Multi-channel**: Notifications via web interface and Telegram

## 🛠️ Technology Stack

### Backend
- **Framework**: Django with Django REST Framework
- **Database**: PostgreSQL (with SQLite fallback for development)
- **Authentication**: Token-based authentication
- **Data Processing**: pandas, numpy for CSV processing
- **Visualization**: matplotlib, plotly for chart generation
- **Containerization**: Docker and Docker Compose

### Frontend
- **Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom components
- **State Management**: React Query for server state, React Context for app state
- **Forms**: React Hook Form with validation
- **Charts**: Chart.js and Recharts for data visualization
- **Internationalization**: i18next with English and Persian support
- **File Upload**: React Dropzone for CSV imports

### Bot
- **Framework**: python-telegram-bot
- **Integration**: Shares backend API with web application

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.10+ (for local backend development)

### Quick Start with Docker

1. **Clone the repository**:
```bash
git clone <repository-url>
cd pennywise-finance-app
```

2. **Start all services**:
```bash
docker-compose up
```

3. **Access the application**:
- Web Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Database: localhost:5432

### Development Setup

#### Backend Development
```bash
cd pennywise_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Frontend Development
```bash
cd frontend
npm install
npm start
```

## 📱 How It Works

### Web Application
1. **Register/Login** to create your account
2. **Upload CSV** transaction files or add transactions manually
3. **Set budgets** for different categories
4. **View dashboard** for real-time financial overview
5. **Generate reports** and download charts
6. **Configure alerts** and notification preferences

### Telegram Bot
1. **Start the bot** in Telegram with `/start`
2. **Upload your CSV** transaction file
3. **Set your budgets** for different categories using simple commands
4. **Receive insights** through automated reports and charts
5. **Stay informed** with real-time budget alerts

## 🔧 Project Structure

```
pennywise-finance-app/
├── pennywise_backend/          # Django backend
│   ├── api/                   # REST API endpoints
│   ├── core/                  # Core models and utilities
│   ├── pennywise/             # Django project settings
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   ├── pages/            # Page components
│   │   ├── contexts/         # React contexts
│   │   ├── services/         # API service layer
│   │   └── utils/            # Utilities and i18n
│   └── package.json          # Node.js dependencies
├── docker-compose.yml         # Multi-service Docker setup
└── README.md                  # This file
```

## 📝 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/users/register/` - User registration

### Transactions
- `GET /api/transactions/` - List transactions
- `POST /api/transactions/` - Create transaction
- `POST /api/transactions/import_csv/` - Import CSV file
- `GET /api/transactions/summary/` - Get transaction summary

### Budgets
- `GET /api/budgets/` - List budgets
- `POST /api/budgets/` - Create budget
- `GET /api/budgets/status/` - Get budget status

### Reports & Charts
- `GET /api/reports/summary/` - Financial summary
- `GET /api/charts/pie/` - Pie chart data
- `GET /api/charts/bar/` - Bar chart data
- `GET /api/charts/line/` - Line chart data

## 🌍 Internationalization

The application supports multiple languages:
- **English** (LTR)
- **Persian/Farsi** (RTL)

Language switching is available in the web interface and persists across sessions.

## 🔒 Security Features

- Token-based authentication
- CORS configuration
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Secure password hashing

## 🚀 Planned Features

- [ ] Multi-currency support
- [ ] Recurring transaction detection
- [ ] Financial goal tracking
- [ ] Export reports to PDF
- [ ] Integration with popular banking APIs
- [ ] Savings recommendations based on spending patterns
- [ ] Bill reminder system
- [ ] Investment tracking capabilities
- [ ] Mobile app (React Native)
- [ ] Advanced analytics and AI insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🎯 Vision

PennyWise aims to make personal finance management accessible, automated, and actionable. By combining modern web technologies with Telegram integration, we're building a comprehensive tool that helps users make informed financial decisions every day.

---

*Built with ❤️ for smarter financial management*