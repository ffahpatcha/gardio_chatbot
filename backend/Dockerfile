# ใช้ Base Image ที่เป็น Python 3.9-slim
FROM python:3.11.9

# กำหนด Working Directory ภายใน Container
WORKDIR /app

# คัดลอกไฟล์ requirements.txt ไปยัง Container
COPY requirements.txt .

# ติดตั้ง Python dependencies ที่ระบุไว้ใน requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมดในโฟลเดอร์ embedding_service ไปยัง Container
COPY . .

# ระบุคำสั่งเริ่มต้นให้รันเมื่อ Container เริ่มทำงาน
CMD ["python", "app.py"]
