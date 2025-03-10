# Docker base image ที่เล็กและเพียงพอสำหรับ Python
FROM python:3.9-slim

# อัปเดต package และติดตั้ง tesseract-ocr (และ libs อื่นๆ ที่จำเป็น)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    # ถ้าใช้ PyMuPDF บางครั้งต้องใช้ libmupdf-dev หรือ poppler-utils
    # ถ้าต้องใช้ poppler-utils สำหรับ PDF บางอย่าง สามารถติดตั้งได้:
    poppler-utils \
    build-essential \
    # อื่นๆ ที่อาจจำเป็นสำหรับการประมวลผล PDF
    && rm -rf /var/lib/apt/lists/*

# กำหนด working directory ใน container
WORKDIR /app

# คัดลอกไฟล์ requirements.txt
COPY requirements.txt .

# ติดตั้ง dependencies จาก requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมดในโปรเจกต์ลง container
COPY . .

# ตั้งค่า environment variable หากต้องการ
# (กรณีต้องการอ่านค่า .env ภายใน Container อาจใช้ python-dotenv ในโค้ดโดยตรง หรือใช้ docker secrets)
# ENV HUGGINGFACE_API_KEY="your-huggingface-key"
# ENV GCS_BUCKET_NAME="pawpal-chatbot"
# ENV GCS_PDF_FOLDER="documents"
# ENV GCS_OUTPUT_FOLDER="faiss_index"
# ENV GOOGLE_APPLICATION_CREDENTIALS="/app/keys/my_service_account.json"

# Expose port ถ้าจำเป็น (หากเป็น script อย่างเดียว อาจไม่ต้อง)
# EXPOSE 8080

# คำสั่งเริ่มต้น เมื่อ container รัน
CMD ["python", "process_pdfs.py"]
