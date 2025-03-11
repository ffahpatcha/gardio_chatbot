import gradio as gr
import requests
###Final

import gradio as gr
import sqlite3
import hashlib

# ========== DB SETUP ==========
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password_hash TEXT
)
""")
conn.commit()

# ========== Helper ==========
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ========== SIGNUP ==========
def handle_signup(username, password):
    if not username or not password:
        return gr.update(visible=True), gr.update(visible=False),"<h4 style='color:red'>❌ Username and password required.</h4>"
    try:
        password_hash = hash_password(password)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
        return gr.update(visible=False), gr.update(visible=True), "<h4 style='color:green'>✅ Signup successful!</h4>"
    except sqlite3.IntegrityError:
        return gr.update(visible=True), gr.update(visible=False), "<h4 style='color:red'>❌ Username already exists.</h4>"

# ========== LOGIN ==========
def handle_login(username, password):
    if not username or not password:
        return gr.update(visible=True), gr.update(visible=False), "<h4 style='color:red'>❌ Username and password required.</h4>"
    password_hash = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, password_hash))
    user = cursor.fetchone()
    if user:
        return gr.update(visible=False), gr.update(visible=True), ""
    else:
        return gr.update(visible=True), gr.update(visible=False), "<h4 style='color:red'>❌ Don't have an account yet? Please sign up first!</h4>"



#chatbot
# === ฟังก์ชันหลักสำหรับการตอบข้อความ ===
# ฟังก์ชันสำหรับเรียก API และดึงคำตอบจาก backend
def get_pet_advice(user_query):
    try:
        payload = {"user_query": user_query}
        # เปลี่ยน URL ให้ตรงกับที่ตั้งของ backend API
        response = requests.post("http://35.247.140.245:8087/generate", json=payload)
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer received.")
        else:
            answer = f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        answer = f"An error occurred: {str(e)}"
    return answer

# === ฟังก์ชันหลักสำหรับการตอบข้อความ ===
def respond(message, history, sessions, current_session):
    history = history or []
    answer = get_pet_advice(message)
    history.append(("user", message))
    history.append(("bot", answer))
    sessions[current_session] = history
    return history, "", sessions, format_chat(history)

# === แปลงประวัติการแชทให้แสดงใน HTML Chatbox ===
def format_chat(history):
    if not history:
        return ""
    formatted = ""
    for sender, msg in history:
        if sender == "user":
            formatted += f"<div class='chat-bubble user'><span>{msg}</span></div>"
        elif sender == "bot":
            formatted += f"<div class='chat-bubble bot'><span>{msg}</span></div>"
    return formatted

def new_chat(sessions):
    new_id = f"Chat {len(sessions) + 1}"
    new_history = [("bot", "สวัสดี! ยินดีต้อนรับสู่ PawPal ฉันคือผู้ช่วยให้คำแนะนำและเทคนิคการแก้ไขปัญหาพฤติกรรมสัตว์เลี้ยง 🐾")]
    sessions[new_id] = new_history
    updated_choices = list(sessions.keys())
    return sessions, new_id, new_history, format_chat(new_history), gr.update(choices=updated_choices, value=new_id)


# === เลือกแชทเก่า ===
def select_session(session_name, sessions):
    history = sessions.get(session_name, [])
    return session_name, history, format_chat(history)

def handle_logout():
    return (
       gr.update(visible=True),    # login_section = แสดง
        gr.update(visible=False),   # chatbot_section = ซ่อน
        gr.update(value=""),        # เคลียร์ login_username
        gr.update(value=""),        # เคลียร์ login_password
        gr.update(value=""),        # เคลียร์ signup_username
        gr.update(value=""),        # เคลียร์ signup_password
        "",                         # เคลียร์ login_result
        ""                          # เคลียร์ signup_result
    )



# === Initial State ===
initial_history = [("bot", "สวัสดี! ยินดีต้อนรับสู่ PawPal ฉันคือผู้ช่วยให้คำแนะนำและเทคนิคการแก้ไขปัญหาพฤติกรรมสัตว์เลี้ยง 🐾")]
initial_sessions = {"Chat 1": initial_history}

# ========== UI ==========
with gr.Blocks(css="""
    html, body, .gradio-container {
    background: linear-gradient(120deg, #ff914d, #ffd0a1, #ffffff);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    font-family: 'Prompt', 'Poppins', 'Kanit', sans-serif !important;
    font-size: 16px;
}
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

    .welcome-title {
    text-align: center;
    margin-top: 40px;
    font-size: 52px;
    font-weight: 800;
    color: transparent;
    background: linear-gradient(to right, #FFA500, #FF7F50, #FFD580);
    -webkit-background-clip: text;
    background-clip: text;
    text-shadow: 2px 2px 10px rgba(255, 153, 0, 0.3);
    letter-spacing: 2px;
    padding-bottom: 10px;
    font-family: 'Fredoka', sans-serif;
}


    .login-box {
        display: flex;
        flex-direction: row;
        width: 700px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        overflow: hidden;
        margin: 30px auto;
        background: linear-gradient(to bottom right, #fffaf3, #fff2e6);
    }
    .login-left {
        width: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    .login-left img {
        width: 100%;
        height: auto;
        justify-content: center;
    }
    .login-right {
        width: 50%;
        padding: 30px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .input-style input {
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #ccc;
        font-size: 16px;
        width: 100%;
        margin-bottom: 15px;
    }
    
    .login-button {
        padding: 12px;
        width: 100%;
        border-radius: 25px;
        background: linear-gradient(to right, #003366, #0066cc);
        color: white;
        font-weight: bold;
        font-size: 16px;
        border: none;
        margin-top: 10px;
        cursor: pointer;
        transition: 0.3s ease-in-out;
        justify-content: center;
    }
    .login-button:hover {
        background: linear-gradient(to right, #002855, #0055aa);
        transform: scale(1.05);
    }
    .signup-text {
        margin-top: 15px;
        text-align: center;
        font-size: 14px;
    }
    .signup-text a {
        color: #ff7f50;
        font-weight: bold;
        text-decoration: none;
    }
    .signup-text a:hover {
        text-decoration: underline;
    }

     #main-box { display: flex; flex-direction: row; height: 100vh; margin: 0; }
    #chatarea { margin-left: 250px; flex: 1; display: flex; justify-content: center; align-items: center; padding: 20px; }
    #chatbox-container
     { width: 95%; max-width: 700px; 
     height: 85vh; background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(15px);
     box-shadow: 0 15px 40px rgba(0,0,0,0.3); border: 1px solid rgba(255, 255, 255, 0.3);
     border-radius: 25px; display: flex; flex-direction: column; overflow: hidden; 
     padding: 10px; }
    #chat-header { background: linear-gradient(90deg, #ff7f50, #ff6a88); color: white; text-align: center; padding: 18px; font-size: 22px; font-weight: bold; border-top-left-radius: 25px; border-top-right-radius: 25px; overflow: hidden; }
   #chat-footer textarea {
    flex: 1;
    border-radius: 25px;
    padding: 14px 20px;
    background: #f0f0f0;
    font-size: 16px;
    height: 46px;
    resize: none;
    box-sizing: border-box;
    margin: 0;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #000 !important; /* ✅ เพิ่มสีข้อความให้ชัดเจน */
}

    #chat-footer textarea { flex: 1; border-radius: 25px; padding: 14px 20px; background: #f0f0f0; font-size: 16px; height: 46px; resize: none; box-sizing: border-box; margin: 0; border: none !important; outline: none !important; box-shadow: none !important; }
    #chat-footer button { 
      height: 46px; min-width: 80px; max-width: 100px; padding: 0 20px; 
      background: linear-gradient(135deg, #ff6a00, #ff944d, #ffd6b3);
 color: white; border: none; 
      font-size: 16px; font-weight: bold; border-radius: 25px; 
      cursor: pointer; transition: background 0.3s ease; }
    #chat-footer button:hover { background: #e06b42; }
    .new-chat-btn {
       margin-top: 10px;  background: linear-gradient(135deg, #ff914d, #ff6a88);

       color: white; padding: 10px; border-radius: 999px; border: none; cursor: pointer; 
       width: 100%; text-align: center; font-weight: bold; font-size: 16px; }
    .new-chat-btn:hover { background: #e06b42; }
    .log-out-btn {
       margin-top: 10px;   background: linear-gradient(135deg, #ffa559, #ffb877, #ffe0c2);


       color: white; padding: 10px; border-radius: 999px; border: none; cursor: pointer; 
       width: 100%; text-align: center; font-weight: bold; font-size: 16px; }
    .log-out-btn:hover { background: #e06b42; }
   

    #sidebar { position: fixed; left: 0; top: 0; width: 250px; height: 100vh; background: white; box-shadow: 2px 0 10px rgba(0,0,0,0.1); padding: 0px 20px 20px 20px; display: flex; flex-direction: column; align-items: center; gap: 10px; }
    .logo-img { width: 200px; height: auto; border-radius: 50%; object-fit: cover; margin-top: 0px; display: block; }
    #chat-display { flex: 1; padding: 20px; overflow-y: auto; }
    .chat-bubble { max-width: 75%; margin: 5px 0; padding: 12px 16px; border-radius: 18px; font-size: 16px; display: inline-block; clear: both; word-wrap: break-word; }
.chat-bubble.bot {
    background: #f0f0f0;
    color: #000;
    float: left;
    text-align: left;
    border-top-left-radius: 0;
}



    .chat-bubble.user { background: #ff7f50; color: white; text-align: right; float: right; border-top-right-radius: 0; }
    #chat-input-box input {
    color: #000 !important;
    background: #f0f0f0 !important;
    
}


""") as demo:
    login_section = gr.Column(visible=True)
    chatbot_section = gr.Column(visible=False)

    with login_section:

        gr.HTML("<h1 class='welcome-title'>Welcome To PawPal</h1>")
        with gr.Tabs():
            with gr.Tab("Login"):
                with gr.Row(elem_classes="login-box"):
                    with gr.Column(elem_classes="login-left"):
                        gr.HTML("<img src='https://raw.githubusercontent.com/Thanwaratrr/picture-isd/main/pawpal.png' alt='PawPal Logo'>")
                    with gr.Column(elem_classes="login-right"):
                        login_username = gr.Textbox(label="Username", placeholder="Enter your username", elem_classes="input-style")
                        login_password = gr.Textbox(label="Password", placeholder="Enter your password", type="password", elem_classes="input-style")
                      
                        login_btn = gr.Button("Login", elem_classes="login-button")
                        
                        login_result = gr.HTML()
                        login_btn.click(fn=handle_login, inputs=[login_username, login_password], outputs=[login_section, chatbot_section, login_result])
                        

            with gr.Tab("Sign Up"):
                with gr.Row(elem_classes="login-box"):
                    with gr.Column(elem_classes="login-left"):
                        gr.HTML("<img src='https://raw.githubusercontent.com/Thanwaratrr/picture-isd/main/pawpal.png' alt='PawPal Logo'>")
                    with gr.Column(elem_classes="login-right"):
                        signup_username = gr.Textbox(label="Username", placeholder="Enter your username", elem_classes="input-style")
                        signup_password = gr.Textbox(label="Password", placeholder="Enter your password", type="password", elem_classes="input-style")
                        signup_btn = gr.Button("Sign Up", elem_classes="login-button")
                        signup_result = gr.HTML()
                        signup_btn.click(fn=handle_signup, inputs=[signup_username, signup_password], outputs=[login_section, chatbot_section, signup_result])
                        
    with chatbot_section:
      with gr.Row(elem_id="main-box"):
        with gr.Column(elem_id="sidebar"):
            gr.HTML("""<img src='https://github.com/Thanwaratrr/picture-isd/raw/main/pawpal.png' class='logo-img'>""")
            session_dropdown = gr.Dropdown(label="ประวัติการแชท", choices=list(initial_sessions.keys()), value="Chat 1")
            new_chat_btn = gr.Button("➕ New Chat", elem_classes="new-chat-btn")
            logout_btn = gr.Button("🚪 Logout", elem_classes="log-out-btn")
            logout_btn.click(
    fn=handle_logout,
    inputs=[],
    outputs=[
        login_section,
        chatbot_section,
        login_username,
        login_password,
        signup_username,
        signup_password,
        login_result,
        signup_result
    ]
)



        with gr.Column(elem_id="chatarea"):
            with gr.Column(elem_id="chatbox-container"):
                gr.HTML("<div id='chat-header'>🐶 Pet Behavior Chatbot 💬</div>")
                chat_display = gr.HTML(value=format_chat(initial_history), elem_id="chat-display", show_label=False)
                history_state = gr.State(value=initial_history)
                sessions_state = gr.State(value=initial_sessions)
                current_session_state = gr.State(value="Chat 1")

                with gr.Row(elem_id="chat-footer"):
                   textbox = gr.Textbox(placeholder="พิมพ์ข้อความ...", lines=1, show_label=False, elem_id="chat-input-box")

                   send_btn = gr.Button("ส่ง")

    #action
    
    send_btn.click(
    fn=respond,
    inputs=[textbox, history_state, sessions_state, current_session_state],
    outputs=[history_state, textbox, sessions_state, chat_display]
).then(
        fn=format_chat,
        inputs=history_state,
        outputs=chat_display
    )

    textbox.submit(
        fn=respond,
        inputs=[textbox, history_state, sessions_state, current_session_state],
        outputs=[history_state, textbox, sessions_state]
    ).then(
        fn=format_chat,
        inputs=history_state,
        outputs=chat_display
    )


    new_chat_btn.click(
        fn=new_chat,
        inputs=[sessions_state],
        outputs=[sessions_state, current_session_state, history_state, chat_display, session_dropdown]
    )

    session_dropdown.change(
        fn=select_session,
        inputs=[session_dropdown, sessions_state],
        outputs=[current_session_state, history_state, chat_display]
    )

demo.launch(server_name="0.0.0.0", server_port=8085, share=False)
