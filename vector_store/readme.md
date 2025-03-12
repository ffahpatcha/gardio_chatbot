# Gardio Chatbot - Vector Store

## Overview
Vector Store ใน Gardio Chatbot ทำหน้าที่เป็นระบบจัดเก็บข้อมูลเวกเตอร์ที่ใช้ในการค้นหาข้อมูลจากเอกสาร ระบบนี้ใช้ FAISS เป็นหลักในการสร้างและดึงข้อมูลที่เกี่ยวข้อง โดยมีโครงสร้างการทำงานดังแผนภาพด้านล่าง:

### Document Processing Pipeline
1. **Local Documents** - โหลดเอกสารจากแหล่งข้อมูลภายในระบบ
2. **Unstructured Loader** - ดึงข้อมูลจากเอกสารที่ไม่มีโครงสร้างแน่นอน
3. **Text** - ได้ข้อมูลเป็นข้อความดิบ
4. **Text Splitter** - แบ่งข้อความออกเป็นส่วนย่อย
5. **Text Chunks** - ข้อความที่ถูกแบ่งออกเป็นส่วนเล็ก ๆ
6. **Embedding** - แปลงข้อความเป็นเวกเตอร์ โดยใช้  https://huggingface.co/BAAI/bge-m3
7. **VectorStore** - จัดเก็บเวกเตอร์เพื่อใช้ในการค้นหาข้อมูล ลง FAISS 

## Folder Structure
```
vector_store/
│── documents/         # เก็บเอกสารที่ใช้เป็นแหล่งข้อมูล
│── faiss_index/       # เก็บไฟล์ดัชนี FAISS
│── load_pdf2.ipynb    # Notebook สำหรับโหลดเอกสาร PDF และแปลงเป็นเวกเตอร์
│── readme.md          # คำอธิบายโปรเจกต์
│── requirements.txt   # รายชื่อ dependencies ที่จำเป็น
```

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/your-repo/gardio_chatbot.git
cd gardio_chatbot/vector store 
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```




