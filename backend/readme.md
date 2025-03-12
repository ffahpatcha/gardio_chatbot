# Backend

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


## API Endpoints
- `POST /generate` - รับ JSON payload ที่มี key `user_query` และคืนคำตอบโดยใช้โมเดลภาษาพร้อมข้อมูลที่ค้นหา

## System Components
- **FAISS Vector Store**: ใช้จัดเก็บเวกเตอร์ของเอกสารสำหรับการค้นหาข้อมูลที่ใกล้เคียง
- **HuggingFace Embeddings ([BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3))**: ใช้สำหรับแปลงข้อความเป็นเวกเตอร์
- **LLM Model ([meta-llama/Llama-3.3-70B-Instruct-Turbo-Free](https://www.together.ai/models/llama-3-3-70b-free))**: ใช้ Together API ในการสร้างคำตอบ

## Document Processing Workflow
1. รับ `user_query` จากผู้ใช้ผ่าน API `/generate`
2. ค้นหาเอกสารที่เกี่ยวข้องผ่าน FAISS
3. สร้าง `context` จากเอกสารที่ดึงมา
4. ใช้ Together API กับโมเดลภาษาสร้างคำตอบ
5. ส่งคำตอบกลับไปยังผู้ใช้

## Notes
- ต้องตั้งค่า `TOGETHER_API_KEY` ในไฟล์ `.env`
