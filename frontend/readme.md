# Frontend

## Overview
Frontend ของ Chatbot ทำหน้าที่เป็นส่วนติดต่อผู้ใช้ (UI) สำหรับโต้ตอบกับระบบ chatbot โดยใช้ Flask เป็น Web Framework สามารถรันได้ผ่าน Python หรือ deploy ด้วย Docker

## Folder Structure
```
frontend/
│── frontend.py        # ไฟล์หลักของ Flask Frontend
│── Dockerfile         # ไฟล์สำหรับสร้าง Docker container
│── requirements.txt   # รายชื่อ dependencies ที่จำเป็น
│── readme.md          # คำอธิบายโปรเจกต์
```

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/ffahpatcha/gardio_chatbot.git
cd gardio_chatbot/frontend
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

## API Communication
Frontend จะทำงานร่วมกับ Backend ผ่าน API โดยส่งคำขอไปยังเซิร์ฟเวอร์ Flask Backend เพื่อประมวลผลและตอบกลับ

## Notes
- ตรวจสอบว่า Backend ทำงานอยู่ก่อนเริ่มใช้งาน Frontend


