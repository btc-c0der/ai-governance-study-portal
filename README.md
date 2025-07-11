---
title: ai-governance
app_file: app.py
sdk: gradio
sdk_version: 5.35.0
---
# 🧠⚖️ AI Governance Architect's Codex

A next-gen AI Governance Study Platform combining curriculum tracking, EU AI Act exploration, ML demos, and AI tutoring.

## 🌟 Features

- 📖 **Curriculum Explorer**: Track your progress through the AI Governance curriculum
- ⚖️ **EU AI Act Explorer**: Interactive exploration of the EU AI Act
- 🤖 **Model Demos**: Hands-on ML model demonstrations
- 🧠 **AI Tutor Chat**: Get help with AI governance concepts
- 📊 **Performance Tracker**: Monitor your learning progress
- 💼 **Annex IV Builder**: Create technical documentation for AI systems
- 🎯 **ISTQB AI Testing**: Prepare for ISTQB AI Testing certification
- 🔐 **Authentication System**: Complete user registration and login with notes management

## 🚀 Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/btc-c0der/ai-governance-study-portal.git
   cd ai-governance-study-portal
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   # or use one of the scripts:
   ./scripts/start.sh
   ```

4. Access the web interface at `http://localhost:7860`

## 📁 Project Structure

```
ai-governance-study-portal/
├── app.py                    # Main application entry point
├── components/               # Core application components
│   ├── auth_manager.py      # Authentication and user management
│   ├── curriculum.py        # Curriculum tracking and notes
│   ├── ai_act_explorer.py   # EU AI Act exploration
│   └── ...
├── data/                    # Database and data files
│   ├── users.db            # User authentication data
│   ├── curriculum_notes.db # Advanced notes (authenticated users)
│   └── progress.db         # Learning progress tracking
├── tests/                   # Test suites
│   ├── test_auth_comprehensive.py
│   ├── test_registration_ui.py
│   └── ...
├── scripts/                 # Setup and deployment scripts
│   ├── start.sh            # Application startup script
│   ├── deploy.py           # Deployment configuration
│   └── ...
├── docs/                    # Documentation
│   ├── AUTHENTICATION_IMPLEMENTATION_COMPLETE.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── ...
└── requirements.txt         # Python dependencies
```

## 🛠️ Tech Stack

- **Frontend**: Gradio 4.x for interactive web interface
- **Backend**: Python with FastAPI integration
- **Database**: SQLite for user data and progress tracking
- **ML/AI**: Scikit-learn, TensorFlow/PyTorch for model demonstrations
- **Data Visualization**: Plotly for interactive charts and graphs
- **Authentication**: Secure user registration and login system
- **Testing**: Comprehensive test suites with pytest

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/test_auth_comprehensive.py
python -m pytest tests/test_registration_ui.py
python -m pytest tests/test_notes_functionality.py
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[Authentication Implementation](docs/AUTHENTICATION_IMPLEMENTATION_COMPLETE.md)** - Complete auth system overview
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[EU AI Act Integration](docs/EU_AI_ACT_INTEGRATION_COMPLETE.md)** - Compliance features
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Technical architecture overview

## 🚀 Deployment

Use the deployment scripts for different environments:

```bash
# Local development
./scripts/start.sh

# Production deployment
python scripts/deploy.py

# Docker deployment
./scripts/start_robust.sh
```

## 📝 License

GBU2 (Good, Bad, Ugly 2.0)

## 🤝 Contact

Author: 0m3g4_k1ng@proton.me 