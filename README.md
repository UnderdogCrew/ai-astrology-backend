# Astrology Platform API

A FastAPI-based backend application for an astrology platform with user registration, authentication, and profile management. Features a modern web interface and comprehensive API documentation.

## 🌟 Features

- **User Registration**: Register with name, email, phone, password, birth details (date, time, location)
- **User Authentication**: JWT-based login system with secure password hashing
- **Profile Management**: Update user profile information
- **MongoDB Integration**: Async MongoDB database with Motor
- **Input Validation**: Comprehensive data validation with Pydantic
- **Security**: Password hashing with bcrypt, JWT tokens, CORS support
- **Modern Web Interface**: Beautiful, responsive UI with Tailwind CSS
- **API Documentation**: Interactive Swagger UI and ReDoc
- **Docker Support**: Complete containerization with Docker Compose

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone and navigate to the project**:
   ```bash
   cd ai-astrology-backend
   ```

2. **Start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Access the application**:
   - Web Interface: http://localhost:3000
   - API Backend: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Local Development

1. **Prerequisites**:
   - Python 3.8+
   - MongoDB (local or cloud instance)
   - pip (Python package manager)

2. **Clone and setup**:
   ```bash
   cd ai-astrology-backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Start the application**:
   ```bash
   # Option A: Use the startup script
   ./start.sh
   
   # Option B: Start manually
   python run.py  # Backend
   python serve_web.py  # Web interface (in another terminal)
   ```

## 📋 Prerequisites

- **Python 3.8+**
- **MongoDB** (local installation or cloud service like MongoDB Atlas)
- **pip** (Python package manager)
- **Docker & Docker Compose** (for containerized deployment)

## 🛠️ Installation

### Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ai-astrology-backend
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=astrology_db
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   APP_NAME=Astrology Platform
   DEBUG=True
   ```

5. **Start MongoDB** (if running locally):
   ```bash
   # macOS with Homebrew
   brew services start mongodb-community
   
   # Ubuntu/Debian
   sudo systemctl start mongod
   
   # Windows
   # Start MongoDB service from Services
   ```

### Docker Setup

1. **Build and start services**:
   ```bash
   docker-compose up -d
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f
   ```

3. **Stop services**:
   ```bash
   docker-compose down
   ```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
# Using startup script
./start.sh

# Manual start
python run.py  # Backend on port 8000
python serve_web.py  # Web interface on port 3000
```

### Production Mode
```bash
# Backend only
uvicorn app.main:app --host 0.0.0.0 --port 8000

# With Docker
docker-compose -f docker-compose.yml up -d
```

## 📚 API Documentation

Once the application is running, you can access:

- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info

### User Management
- `GET /users/profile` - Get user profile
- `PUT /users/profile` - Update user profile
- `DELETE /users/profile` - Delete user profile (soft delete)

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

## 📝 Example Usage

### Register a new user
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "1234567890",
    "password": "securepassword123",
    "birthdate": "1990-05-15",
    "birthtime": "14:30",
    "birth_location": "New York, NY, USA"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword123"
  }'
```

### Update profile (requires authentication)
```bash
curl -X PUT "http://localhost:8000/users/profile" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith",
    "birth_location": "Los Angeles, CA, USA"
  }'
```

## 📊 Data Models

### User Registration
- `name`: Full name (2-100 characters)
- `email`: Valid email address
- `phone_number`: Phone number (10-15 characters)
- `password`: Password (minimum 8 characters)
- `birthdate`: Date of birth (YYYY-MM-DD format)
- `birthtime`: Time of birth (HH:MM format)
- `birth_location`: Location of birth (2-200 characters)

### User Update
All fields are optional for updates.

## 🔒 Security Features

- **Password Hashing**: Passwords are hashed using bcrypt
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive validation using Pydantic
- **CORS Support**: Configurable CORS middleware
- **Security Headers**: XSS protection, content type options, etc.

## 🏗️ Project Structure

```
ai-astrology-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── auth.py              # Authentication utilities
│   ├── dependencies.py      # Dependency injection
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # User data models
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Authentication routes
│       └── users.py         # User management routes
├── web/
│   ├── index.html           # Web interface
│   └── script.js            # Frontend JavaScript
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
├── run.py                  # Application runner
├── serve_web.py            # Web interface server
├── start.sh                # Startup script
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── nginx.conf              # Nginx configuration
└── README.md               # This file
```

## 🐳 Docker Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
# Build production image
docker build -t astrology-platform .

# Run with production environment
docker run -d \
  -p 8000:8000 \
  -e MONGODB_URL=mongodb://your-mongodb-url \
  -e SECRET_KEY=your-production-secret \
  -e DEBUG=False \
  astrology-platform
```

## 🧪 Testing

### Manual Testing
1. Start the application
2. Open http://localhost:3000 in your browser
3. Register a new user
4. Login with the created credentials
5. Test profile updates

### API Testing
1. Use the Swagger UI at http://localhost:8000/docs
2. Test endpoints with curl commands
3. Use tools like Postman or Insomnia

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DATABASE_NAME` | Database name | `astrology_db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `APP_NAME` | Application name | `Astrology Platform` |
| `DEBUG` | Debug mode | `True` |

### MongoDB Configuration

For production, consider using MongoDB Atlas or a managed MongoDB service:

```env
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/astrology_db
```

## 🚀 Deployment

### Heroku
1. Create a `Procfile`:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. Set environment variables in Heroku dashboard

3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### AWS/GCP/Azure
Use the provided Dockerfile and docker-compose.yml for container deployment.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the logs: `docker-compose logs` or application logs
2. Verify MongoDB is running and accessible
3. Check environment variables are correctly set
4. Open an issue on GitHub with detailed error information

## 🔮 Future Enhancements

- [ ] Birth chart calculations and interpretations
- [ ] Horoscope generation
- [ ] Compatibility matching
- [ ] Email notifications
- [ ] Admin dashboard
- [ ] Mobile app support
- [ ] Multi-language support
- [ ] Advanced astrology features

---

**Made with ❤️ for the astrology community**