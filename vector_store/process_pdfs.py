import os
import re
import unicodedata
from tqdm import tqdm
from PIL import Image
import fitz  # PyMuPDF
import pytesseract
import PyPDF2
from dotenv import load_dotenv
from google.cloud import storage
import shutil
import tempfile

# สำหรับ LangChain และ Transformers
from langchain.schema import Document as LangchainDocument
from langchain.docstore.document import Document  # ใช้ Document ของ LangChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings as LCHuggingFaceEmbeddings
from transformers import AutoTokenizer
from huggingface_hub import login

# โหลด environment variables
load_dotenv()
api_key = os.getenv("HUGGINGFACE_API_KEY")

# -------------------- แก้ไขส่วนนี้ให้ตรงกับ GCS ของคุณ --------------------
# ชื่อ bucket ที่เก็บ PDF
GCS_BUCKET_NAME = "pawpal-chatbot"

# โฟลเดอร์ใน bucket ที่เก็บไฟล์ PDF
# ถ้าภายใน bucket มีโฟลเดอร์ชื่อ documents ให้ใส่ "documents"
# ถ้าไม่มีโฟลเดอร์ ใช้เป็น "" (ค่าว่าง) ก็ได้
GCS_PDF_FOLDER = "documents"

# โฟลเดอร์หรือ path สำหรับบันทึก FAISS index (เช่น "faiss_index")
# ถ้าต้องการบันทึกที่ root ของ bucket ให้กำหนดเป็น ""
GCS_OUTPUT_FOLDER = "faiss_index"
# --------------------------------------------------------------------------

# กำหนดพาธไปยัง Tesseract (สำหรับ Windows)
if os.name == 'nt':
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    else:
        print(f"Tesseract ไม่พบที่ {tesseract_path}. กรุณาติดตั้ง Tesseract OCR และตรวจสอบ PATH.")

# ฟังก์ชันดึงข้อความและ metadata จาก PDF ด้วย PyPDF2
def extract_text_from_pdf_with_metadata(pdf_path):
    text = ""
    metadata = {}
    try:
        pdf_path = os.path.normpath(pdf_path)
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            metadata = reader.metadata or {}
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
    return text, metadata

# ฟังก์ชันทำความสะอาดข้อความ (ลบเว้นวรรคส่วนเกิน)
def clean_text(text):
    return " ".join(text.split())

# ฟังก์ชัน post-process สำหรับข้อความภาษาไทย
def postprocess_thai_text(text):
    return re.sub(r'(?<=[\u0E00-\u0E7F])\s+(?=[\u0E00-\u0E7F])', '', text)

# ฟังก์ชันใช้ OCR ดึงข้อความจาก PDF ด้วย PyMuPDF
def ocr_pdf_with_pymupdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            pix = page.get_pixmap(dpi=300)
            mode = "RGB" if pix.alpha == 0 else "RGBA"
            img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
            page_text = pytesseract.image_to_string(img, lang='tha')
            text += page_text + "\n"
        doc.close()
    except Exception as e:
        print(f"Error during OCR with PyMuPDF on {pdf_path}: {e}")
    return text

# ตัวแปรสำหรับแยกข้อความเป็นชิ้น
MARKDOWN_SEPARATORS = [
    "\n#{1,6} ",
    "```\n",
    "\n\\*\\*\\*+\n",
    "\n---+\n",
    "\n___+\n",
    "\n\n",
    "\n",
    " ",
    "",
]

def split_documents(chunk_size, knowledge_base, tokenizer_name="BAAI/bge-m3"):
    try:
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=True)
    except Exception as e:
        print(f"❌ Error loading tokenizer: {e}")
        return []

    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer,
        chunk_size=chunk_size,
        chunk_overlap=int(chunk_size / 10),
        add_start_index=True,
        strip_whitespace=True,
        separators=MARKDOWN_SEPARATORS,
    )

    docs_processed = []
    for doc in knowledge_base:
        docs_processed += text_splitter.split_documents([doc])

    unique_texts = {}
    docs_processed_unique = []
    for doc in docs_processed:
        if doc.page_content not in unique_texts:
            unique_texts[doc.page_content] = True
            docs_processed_unique.append(doc)

    return docs_processed_unique

# ฟังก์ชันสำหรับดาวน์โหลดไฟล์ PDF จาก GCS
def download_pdfs_from_gcs(local_dir):
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    
    # สร้าง prefix จาก GCS_PDF_FOLDER
    # ถ้า GCS_PDF_FOLDER เป็น "" จะได้ prefix = ""
    prefix = GCS_PDF_FOLDER.strip("/")
    if prefix:
        prefix += "/"
    
    # list_blobs(prefix=...) เพื่อค้นหาไฟล์ PDF
    blobs = bucket.list_blobs(prefix=prefix)
    
    local_files = []
    os.makedirs(local_dir, exist_ok=True)
    for blob in blobs:
        if blob.name.endswith(".pdf"):
            filename = os.path.basename(blob.name)
            local_path = os.path.join(local_dir, filename)
            blob.download_to_filename(local_path)
            print(f"Downloaded {blob.name} to {local_path}")
            local_files.append(local_path)
    return local_files

# ฟังก์ชันอัปโหลดโฟลเดอร์ไปยัง GCS (อัปโหลดไฟล์ทีละไฟล์)
def upload_directory_to_gcs(local_dir, gcs_destination_folder):
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)

    # กำหนด prefix ของ folder ปลายทาง
    # ถ้า gcs_destination_folder เป็น "" จะอัปโหลดไฟล์ไปที่ root
    prefix = gcs_destination_folder.strip("/")
    # ถ้า prefix ไม่ใช่ค่าว่าง ให้เติม "/" ท้าย prefix
    if prefix:
        prefix += "/"

    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_dir)
            destination_blob_name = prefix + relative_path  # path ใน GCS
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(local_path)
            print(f"Uploaded {local_path} to {destination_blob_name}")

def main():
    # สร้าง temporary directory สำหรับเก็บไฟล์ PDF ที่ดาวน์โหลดและผลลัพธ์ FAISS
    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_local_dir = os.path.join(tmp_dir, "pdfs")
        os.makedirs(pdf_local_dir, exist_ok=True)
        
        # ดาวน์โหลดไฟล์ PDF จาก GCS
        print("Downloading PDF files from GCS...")
        pdf_files = download_pdfs_from_gcs(pdf_local_dir)
        if not pdf_files:
            print("ไม่พบไฟล์ PDF ใน bucket ที่ระบุ")
            return

        RAW_KNOWLEDGE_BASE = []
        print("Processing PDFs ...")
        for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
            text, metadata = extract_text_from_pdf_with_metadata(pdf_file)
            if not text.strip():
                print(f"No text extracted from {pdf_file}, trying OCR...")
                text = ocr_pdf_with_pymupdf(pdf_file)
            cleaned_text = clean_text(text)
            doc = Document(page_content=cleaned_text, metadata={"source": pdf_file, "details": metadata})
            RAW_KNOWLEDGE_BASE.append(doc)

        print(f"\nจำนวนเอกสารใน RAW_KNOWLEDGE_BASE: {len(RAW_KNOWLEDGE_BASE)}")
        if len(RAW_KNOWLEDGE_BASE) > 0:
            print(f"ตัวอย่างเนื้อหาในเอกสารแรก:\n{RAW_KNOWLEDGE_BASE[0].page_content[:300]}")

        # ตรวจสอบให้แน่ใจว่า RAW_KNOWLEDGE_BASE เป็นลิสต์ของ Document
        if not isinstance(RAW_KNOWLEDGE_BASE, list):
            RAW_KNOWLEDGE_BASE = [RAW_KNOWLEDGE_BASE]
        else:
            RAW_KNOWLEDGE_BASE = [
                doc if isinstance(doc, Document) else Document(page_content=str(doc))
                for doc in RAW_KNOWLEDGE_BASE
            ]

        # แบ่งเอกสารเป็นชิ้น
        docs_processed = split_documents(
            512,  # ขนาด chunk
            RAW_KNOWLEDGE_BASE,
            tokenizer_name="BAAI/bge-m3",
        )

        if docs_processed:
            print(f"✅ แบ่งเอกสารได้ {len(docs_processed)} ชิ้น")
        else:
            print("❌ ไม่พบข้อมูล หรือมีปัญหาในการแบ่งเอกสาร")
            return

        # ล็อกอิน HuggingFace ด้วย access token
        login(api_key)

        EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
        embedding_model = LCHuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            multi_process=True,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

        if not docs_processed:
            raise ValueError("docs_processed ไม่มีข้อมูล กรุณาตรวจสอบเอกสารก่อนสร้าง FAISS index")

        # สร้าง FAISS index
        KNOWLEDGE_VECTOR_DATABASE = FAISS.from_documents(
            docs_processed, embedding_model, distance_strategy=DistanceStrategy.COSINE
        )

        # บันทึก FAISS index ลงใน temporary directory
        faiss_local_dir = os.path.join(tmp_dir, "faiss_index")
        KNOWLEDGE_VECTOR_DATABASE.save_local(faiss_local_dir)
        print("✅ FAISS index ถูกบันทึกใน temporary directory แล้ว.")

        # อัปโหลด FAISS index ที่ได้กลับไปยัง GCS
        print("Uploading FAISS index to GCS...")
        upload_directory_to_gcs(faiss_local_dir, GCS_OUTPUT_FOLDER)
        print("✅ FAISS index ถูกอัปโหลดไปยัง GCS เรียบร้อยแล้ว.")

if __name__ == "__main__":
    main()
