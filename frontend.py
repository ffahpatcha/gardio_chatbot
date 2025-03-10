import gradio as gr
import requests

# ฟังก์ชันสำหรับเรียก API และดึงคำตอบจาก backend
def get_pet_advice(user_query):
    try:
        payload = {"user_query": user_query}
        # เปลี่ยน URL ให้ตรงกับที่ตั้งของ backend API ถ้ารันบนเครื่องอื่นให้ระบุ IP และ port ที่ถูกต้อง
        response = requests.post("http://127.0.0.1:5000/generate", json=payload)
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer received.")
        else:
            answer = f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        answer = f"An error occurred: {str(e)}"
    return answer

# สร้าง Interface ด้วย Gradio
iface = gr.Interface(
    fn=get_pet_advice,
    inputs=gr.Textbox(lines=3, placeholder="พิมพ์คำถามหรือรายงานเกี่ยวกับพฤติกรรมสัตว์เลี้ยงของคุณที่นี่...", label="Pet Query"),
    outputs=gr.Textbox(label="คำตอบ"),
    title="คำแนะนำด้านพฤติกรรมสัตว์เลี้ยง",
    description="กรุณาพิมพ์คำถามหรือรายงานเกี่ยวกับพฤติกรรมสัตว์เลี้ยงของคุณ แล้วระบบจะให้คำแนะนำในแบบที่เป็นมิตรและเข้าใจง่าย"
)

if __name__ == "__main__":
    iface.launch()
