# Gardio Chatbot - Backend

## Overview
Backend ของ Gardio Chatbot ทำหน้าที่เป็นเซิร์ฟเวอร์สำหรับให้บริการ API ที่เกี่ยวข้องกับการค้นหาข้อมูลเวกเตอร์โดยใช้ FAISS และการประมวลผลข้อความเพื่อโต้ตอบกับ chatbot ระบบนี้รองรับการทำงานผ่าน Flask API และสามารถ deploy ได้ผ่าน Docker

## Folder Structure
```
backend/
│── faiss_index/       # เก็บไฟล์ดัชนี FAISS และ pickle
│── app.py             # ไฟล์หลักของ Flask API
│── Dockerfile         # ไฟล์สำหรับสร้าง Docker container
│── requirements.txt   # รายชื่อ dependencies ที่จำเป็น
│── readme.md          # คำอธิบายโปรเจกต์
```

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/ffahpatcha/gardio_chatbot.git
cd gardio_chatbot/backend
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Backend Server

ใช้ Docker:
```bash
docker build -t gardio-backend .
docker run -p 5000:5000 gardio-backend
```

## FAISS Index
ไฟล์ `faiss_index/index.faiss` และ `faiss_index/index.pkl` ใช้สำหรับเก็บเวกเตอร์ที่ใช้ในกระบวนการค้นหาคล้ายกัน (vector search)

## API Endpoints
- `POST /generate` - ส่งข้อความค้นหาเพื่อให้ chatbot ตอบกลับโดยใช้ FAISS
