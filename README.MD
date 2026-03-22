# 🚀 AI-Powered Learning & Career Platform

An end-to-end **Full Stack AI SaaS Platform** built with **Django REST Framework + React.js**, designed to deliver an interactive learning experience with **AI assistance, real-time chat, and secure payments**.

🔗 **Live Demo:** https://your-frontend.onrender.com
🔗 **Backend API:** https://your-backend.onrender.com

---

## 📌 Overview

This platform allows users to:

* 📚 Browse and enroll in courses
* 🤖 Get AI-powered career guidance
* 📄 Analyze resumes using AI
* 💬 Communicate in real-time chat
* 💳 Purchase courses securely

Built with **scalability, performance, and real-world architecture** in mind.

---

## 🧠 Key Features

### 🔐 Authentication & User System

* JWT-based authentication (Login/Register)
* Role-based access (Student / Instructor)
* Protected routes & secure APIs

### 📚 Course Platform

* Course creation (Instructor only)
* Course listing with pagination, search, filtering
* Course detail with lessons
* Enrollment system with progress tracking

### 🤖 AI Integration

* AI Chatbot for career guidance
* Resume Analyzer (PDF upload + AI feedback)
* Smart responses using OpenAI API

### 💬 Real-Time System

* Live chat using WebSockets (Django Channels)
* Instant message broadcasting

### 💳 Payment System

* Razorpay integration
* Secure course purchase flow
* Auto enrollment after payment

### 📊 Dashboard

* My Courses page
* Progress tracking system
* Real-time UI updates

---

## 🏗️ Tech Stack

### 🔹 Backend

* Python
* Django
* Django REST Framework (DRF)
* MySQL / PostgreSQL
* Django Channels (WebSockets)
* Redis (Caching)

### 🔹 Frontend

* React.js (Vite)
* Redux Toolkit (RTK)
* Tailwind CSS
* Axios

### 🔹 AI & Integrations

* OpenAI API
* Razorpay Payment Gateway

### 🔹 DevOps & Deployment

* Render (Backend + Frontend)
* Docker (Optional)
* Gunicorn + Whitenoise

---

## 📁 Project Structure

### Backend

```
backend/
 ┣ accounts/
 ┣ courses/
 ┣ ai_services/
 ┣ core/
 ┣ config/
```

### Frontend

```
frontend/
 ┣ src/
 ┃ ┣ app/
 ┃ ┣ features/
 ┃ ┣ pages/
 ┃ ┣ components/
 ┃ ┣ services/
```

---

## ⚙️ Installation & Setup

### 🔹 Backend Setup

```bash
git clone https://github.com/your-username/project.git
cd backend

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

### 🔹 Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

---

## 🔐 Environment Variables

Create `.env` file in backend:

```
SECRET_KEY=your_secret_key
DEBUG=True
OPENAI_API_KEY=your_openai_key
RAZORPAY_KEY_ID=your_key
RAZORPAY_KEY_SECRET=your_secret
DATABASE_URL=your_database_url
```

---

## 🧪 Testing

### Backend

```bash
python manage.py test
```

---

## 🐳 Docker (Optional)

```bash
docker-compose up --build
```

---

## 📸 Screenshots

*Add screenshots here (Home, Dashboard, Chat, Payment, Resume Analyzer)*

---

## 🚀 Future Improvements

* AI-based course recommendations
* Dark mode
* Notifications system
* Advanced analytics dashboard
* Mobile responsiveness improvements

---

## 💼 Resume Highlight

> Built a scalable AI-powered learning platform using Django, DRF, React, and Redux Toolkit with features like JWT authentication, real-time chat (WebSockets), AI chatbot, resume analyzer, and Razorpay payment integration. Deployed on Render with production-ready architecture, caching (Redis), and Docker support.

---

## 👨‍💻 Author

**Sonu Kumar**

* GitHub: https://github.com/your-username
* LinkedIn: https://linkedin.com/in/your-profile

---

## ⭐ If you like this project

Give it a ⭐ on GitHub and share it!

---
