title: RiskIQ Backend
emoji: 📈
colorFrom: indigo
colorTo: purple
sdk: docker
sdk_version: "1.0"
pinned: false
license: mit

# 🧠 RiskIQ Backend

This is the **backend API** for the RiskIQ project — a Python-based system that provides stock data, analytics, and risk assessment services.  
It is deployed on **Hugging Face Spaces** using **Docker** for full control over dependencies and environment.

---

## 🚀 Features
- FastAPI-powered RESTful API  
- Real-time stock data via **yfinance**  
- Financial analytics using **pandas** and **numpy**  
- Deployed entirely **for free** on Hugging Face Spaces  

---

## 🧩 Deployment
This app is containerized with Docker and runs on port **7860** (default Hugging Face Space port).

# RiskIQ Backend

This is the backend for the RiskIQ project, deployed as a Docker Space on Hugging Face.

### Run locally
```bash
# Build Docker image
docker build -t riskiq-backend .

# Run container
docker run -p 7860:7860 riskiq-backend
