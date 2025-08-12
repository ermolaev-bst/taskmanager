# 🚀 TaskManager - Corporate Task Management System

## 📋 Project Description

**TaskManager** is a modern web system for automating IT department task management, developed on Python Flask. The system replaces manual request tracking and provides efficient workflow management.

## ✨ Key Features

- **🎯 Task Management** - Create, track and manage requests
- **👥 Role-based System** - Access control by roles (User, IT Staff, Administrator)
- **📱 Telegram Integration** - Instant notifications about new requests and status changes
- **📊 Analytics & Reports** - Detailed statistics on tasks and performance
- **🔐 Security** - User authentication and authorization
- **📁 File Management** - Upload and store request attachments
- **🌐 Web Interface** - Modern responsive design

## 🏗️ System Architecture

### User Roles

1. **Users**
   - Create new requests
   - View status of their requests
   - Receive notifications about changes

2. **IT Staff**
   - Accept requests for work
   - Change task status
   - Receive notifications about new requests

3. **Administrators**
   - Full system access
   - User management
   - View all requests and statistics
   - System configuration

### Technical Stack

- **Backend**: Python 3.8+, Flask
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Notifications**: Telegram Bot API
- **Deployment**: Docker, Docker Compose

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/ermolaev-bst/taskmanager.git
   cd taskmanager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with necessary parameters
   ```

5. **Initialize database**
   ```bash
   python setup_database.py
   ```

6. **Run application**
   ```bash
   python app.py
   ```

Application will be available at: http://localhost:5000

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Main settings
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///taskmanager_dev.db

# Telegram settings
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Security settings
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
```

### Telegram Bot Setup

1. Create a bot via @BotFather in Telegram
2. Get bot token
3. Add bot to required chat
4. Get Chat ID
5. Specify data in system settings

## 📱 Using the System

### Creating a Request

1. Go to main page
2. Click "Create Request"
3. Fill out the form:
   - Task title
   - Description
   - Priority
   - Category
   - Attachments (files)
4. Click "Submit"

### Task Management (IT Staff)

1. Log in with IT staff account
2. View list of new requests
3. Accept task for work
4. Update status as you progress
5. Complete the task

### Administration

1. Log in with administrator account
2. Manage users
3. Configure system parameters
4. View statistics and reports

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

### Manual Docker Build

```bash
# Build image
docker build -t taskmanager .

# Run container
docker run -p 5000:5000 taskmanager
```

## 📊 API Endpoints

### Tasks
- `GET /api/tasks` - Task list
- `POST /api/tasks` - Create task
- `GET /api/tasks/<id>` - Task details
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task

### Users
- `GET /api/users` - User list
- `POST /api/users` - Create user
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Delete user

### Analytics
- `GET /api/analytics/overview` - General statistics
- `GET /api/analytics/departments` - Department statistics
- `GET /api/analytics/performance` - Performance metrics

## 🔧 Development

### Project Structure

```
taskmanager/
├── app.py                 # Main Flask application
├── config.py             # Configuration
├── requirements.txt      # Python dependencies
├── setup_database.py    # Database initialization script
├── models/              # Data models
├── services/            # Business logic
├── templates/           # HTML templates
├── static/              # Static files (CSS, JS)
├── utils/               # Helper functions
├── database/            # Database migrations and schemas
└── routes/              # Additional routes
```

### Adding New Features

1. Create model in `models/`
2. Add service in `services/`
3. Create API endpoint in `app.py`
4. Add template in `templates/`
5. Update documentation

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

### API Testing

```bash
# Test task creation
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task","description":"Description"}'
```

## 📝 Changelog

Detailed information about changes in [CHANGELOG.md](CHANGELOG.md)

## 🚀 Development Plans

- [ ] Integration with external systems (Jira, Trello)
- [ ] Mobile application
- [ ] Advanced analytics and reports
- [ ] Task comment system
- [ ] Automatic reminders
- [ ] Data export to various formats

## 🤝 Contributing

We welcome contributions to project development! Please:

1. Fork the repository
2. Create a branch for new feature
3. Make changes
4. Create Pull Request

## 📄 License

This project is distributed under MIT license. See LICENSE file for details.

## 📞 Support

If you have questions or issues:

- Create Issue in GitHub
- Refer to documentation
- Check [QUICK_START.md](QUICK_START.md)

---

**TaskManager** - Simplifying IT department task management! 🚀
