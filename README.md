# AI Personal Finance Autopilot

A production-ready full-stack web application that uses AI to automatically analyze bank statements, categorize transactions, generate insights, predict future expenses, and provide actionable financial recommendations.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Features

### Core Functionality
- **Bank Statement Upload**: Support for CSV and PDF files with automatic column detection
- **Smart Categorization**: Hybrid AI system combining rule-based patterns and machine learning
- **Transaction Management**: View, filter, and manually override transaction categories
- **Interactive Dashboard**: Real-time visualizations of income, expenses, and cashflow trends

### AI-Powered Features
- **Financial Insights**: Automatically detect spending anomalies, patterns, and recurring subscriptions
- **Expense Predictions**: Forecast next month's expenses using rolling averages and trend analysis
- **Action Recommendations**: Get personalized advice on budgets, subscriptions, and savings opportunities
- **Confidence Scoring**: Every AI output includes confidence levels and explanations

### Technical Highlights
- Secure authentication with JWT tokens
- Duplicate transaction detection
- Learning from user overrides
- Responsive dark mode UI
- RESTful API with FastAPI
- Type-safe frontend with TypeScript

## 🧱 Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **SQLAlchemy** - ORM for database management
- **PostgreSQL/SQLite** - Database (SQLite for local dev)
- **Pandas** - Data processing and analysis
- **PyPDF** - PDF parsing
- **Passlib & JWT** - Authentication and security

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization
- **Axios** - HTTP client

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

## 🚀 Installation & Setup

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. (Optional) Set environment variables:
```bash
# Create a .env file in the backend directory
DATABASE_URL=sqlite:///./finance_tracker.db  # Or your PostgreSQL URL
SECRET_KEY=your-secret-key-change-this-in-production
```

5. Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. (Optional) Configure environment:
```bash
# Create a .env.local file
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 📊 Example Bank Statement Format

### CSV Format

The application auto-detects CSV columns. Here's an example format:

```csv
Date,Description,Debit,Credit
2024-01-15,Starbucks Coffee,-5.50,
2024-01-16,Salary Deposit,,3500.00
2024-01-17,Uber Ride,-12.30,
2024-01-18,Amazon Purchase,-45.99,
2024-01-19,Netflix Subscription,-15.99,
```

Alternative formats are also supported:
- Single "Amount" column (negative for debits)
- Different date formats (MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD)
- Different column names (the system auto-detects)

See `docs/sample-statement.csv` for a complete example.

### PDF Format

The application can parse PDF bank statements using pattern matching. It supports common formats from major banks.

## 🎨 Usage Guide

### 1. Registration & Login
- Create an account with email and password (min 8 characters)
- Login to access your dashboard

### 2. Upload Bank Statement
- Go to Dashboard
- Drag & drop or click to upload CSV/PDF file
- System automatically parses and categorizes transactions
- Duplicates are automatically detected and skipped

### 3. View Transactions
- Navigate to "Transactions" page
- View all transactions with categories and amounts
- Click "Edit" to override category (system learns from your changes)

### 4. Explore Dashboard
- View monthly summary cards (Income, Expenses, Savings)
- Analyze spending by category (pie chart)
- Track cashflow trends over time (line chart)

### 5. Generate Insights
- Navigate to "Insights" page
- Click "Regenerate Insights" to run AI analysis
- Review detected anomalies, trends, and patterns
- Each insight includes AI reasoning and confidence score

### 6. View Predictions
- Navigate to "Predictions" page
- See forecasts for next month's expenses, income, and savings
- Review category-level predictions
- Read detailed explanations of prediction methodology

### 7. Get Recommendations
- Navigate to "Recommendations" page
- Review personalized action items
- See estimated financial impact
- Understand the rationale behind each suggestion

## 🏗️ Project Structure

```
ai-personal-finance-autopilot/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── api/                    # API endpoints
│   │   │   ├── auth.py            # Authentication routes
│   │   │   ├── transactions.py    # Transaction management
│   │   │   ├── dashboard.py       # Dashboard data
│   │   │   ├── insights.py        # AI insights
│   │   │   ├── predictions.py     # Predictions
│   │   │   └── recommendations.py # Recommendations
│   │   ├── models/                 # Database models
│   │   │   ├── base.py            # Database setup
│   │   │   ├── user.py
│   │   │   ├── transaction.py
│   │   │   ├── category.py
│   │   │   ├── insight.py
│   │   │   └── prediction.py
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── services/               # Business logic
│   │   ├── ai/                     # AI engines
│   │   │   ├── categorizer.py     # Transaction categorization
│   │   │   ├── insights.py        # Insight generation
│   │   │   ├── predictions.py     # Expense prediction
│   │   │   └── recommendations.py # Action recommendations
│   │   └── utils/                  # Utilities
│   │       ├── auth.py            # JWT & password hashing
│   │       ├── csv_parser.py      # CSV parsing
│   │       └── pdf_parser.py      # PDF parsing
│   └── requirements.txt
│
├── frontend/
│   ├── app/                        # Next.js App Router pages
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Home page
│   │   ├── login/
│   │   ├── register/
│   │   ├── dashboard/
│   │   ├── transactions/
│   │   ├── insights/
│   │   ├── predictions/
│   │   └── recommendations/
│   ├── components/                 # React components
│   │   ├── FileUpload.tsx
│   │   ├── DashboardCharts.tsx
│   │   └── Navbar.tsx
│   ├── lib/                        # Utilities & hooks
│   │   ├── api.ts                 # API client
│   │   ├── auth-context.tsx       # Auth provider
│   │   └── utils.ts               # Helper functions
│   ├── styles/
│   │   └── globals.css
│   ├── package.json
│   └── next.config.js
│
├── docs/
│   └── sample-statement.csv        # Example CSV file
└── README.md
```

## 🔒 Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **JWT Authentication**: Token-based session management
- **CORS Protection**: Configured for frontend-backend communication
- **Input Validation**: Pydantic schemas validate all API inputs
- **SQL Injection Prevention**: SQLAlchemy ORM protects against SQL injection

## 🧪 API Endpoints

### Authentication
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user info

### Transactions
- `POST /transactions/upload` - Upload bank statement
- `GET /transactions/` - Get user's transactions
- `PATCH /transactions/{id}` - Update transaction category

### Dashboard
- `GET /dashboard/` - Get dashboard data

### Insights
- `POST /insights/generate` - Generate AI insights
- `GET /insights/` - Get all insights

### Predictions
- `POST /predictions/generate` - Generate predictions
- `GET /predictions/` - Get all predictions

### Recommendations
- `GET /recommendations/` - Get actionable recommendations

Full API documentation available at `http://localhost:8000/docs`

## 🎨 UI Features

- **Dark Mode**: Automatic dark mode support
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Gradient Backgrounds**: Modern, premium aesthetics
- **Interactive Charts**: Hover for detailed data
- **Loading States**: Smooth loading indicators
- **Error Handling**: User-friendly error messages

## 🚧 Future Enhancements

- Multi-currency support
- Budget goal tracking
- Email notifications for insights
- Export reports to PDF
- Integration with banking APIs
- Mobile app (React Native)
- Advanced ML models for categorization
- Multi-user household accounts

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 👨‍💻 Development

### Running Tests
```bash
# Backend tests (coming soon)
cd backend
pytest

# Frontend tests (coming soon)
cd frontend
npm test
```

### Building for Production

Backend:
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

Frontend:
```bash
npm run build
npm start
```

## 🐛 Troubleshooting

**Issue**: Backend won't start
- Ensure Python 3.9+ is installed
- Check if port 8000 is available
- Verify all dependencies are installed

**Issue**: Frontend won't connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Verify API URL in frontend configuration

**Issue**: CSV parsing fails
- Check CSV format matches expected structure
- Ensure date column is recognizable
- Try the example CSV file first

## 💬 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, Next.js, and AI
# AI-Personal-Finance-Autopilot
