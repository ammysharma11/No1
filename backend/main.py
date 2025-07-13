"""
FastAPI entry-point – **without Langfuse**.
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from tempfile import NamedTemporaryFile
from langchain_core.messages import HumanMessage
import os

from graph import react_graph
from tools import send_html_email

app = FastAPI()

# ───────────  CORS so the React dev-server can call the API  ───────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────────  /process/  ───────────────────────────────────────────────
@app.post("/process/")
async def process(
    prompt:   str               = Form(...),
    subject:  str               = Form(...),
    receiver: str               = Form(...),
    file:     UploadFile | None = File(None),
):
    """Run the LangGraph agent and (optionally) send the e-mail."""
    # 1. save uploaded file (if any)
    img_path = None
    if file:
        ext = os.path.splitext(file.filename)[1] or ".bin"
        with NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(await file.read())
            img_path = tmp.name

    # 2. build state for LangGraph
    state = {
        "messages"  : [HumanMessage(content=prompt)],
        "input_file": img_path,
        "receiver"  : receiver,
        "subject"   : subject,
    }

    # 3. run the state machine
    state_out = react_graph.invoke(state)
    answer    = state_out["messages"][-1].content

    # 4. e-mail via SendGrid
    email_status = send_html_email(answer, receiver, subject=subject)

    # 5. cleanup temp file
    if img_path and os.path.exists(img_path):
        os.remove(img_path)

    return JSONResponse({"result": answer, "email_status": email_status})
