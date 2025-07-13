import base64, os, re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()                    # read .env once at import time
GOOGLE_API_KEY  = os.getenv("GOOGLE_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# ───────── Vision / LLM objects ─────────
vision_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=GOOGLE_API_KEY,
)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=GOOGLE_API_KEY,
)

# ───────── helper tools ─────────
def divide(a: int, b: int) -> float:
    """Divide *a* by *b* and return the result."""
    return a / b


def extract_text(img_path: str) -> str:
    """
    Extract all text from a (PNG/JPG/PDF) image using Gemini Vision.

    Args:
        img_path: local image path.

    Returns:
        Extracted text.
    """
    try:
        with open(img_path, "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode()

        response = vision_llm.invoke([
            HumanMessage(
                content=[
                    {"type": "text",
                     "text": "Extract all text in this image. "
                             "Return text only, no explanations."},
                    {"type": "image_url",
                     "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                ]
            )
        ])
        return response.content.strip()
    except Exception as e:
        return f"❌ Vision error: {e}"


def send_html_email(
    html_body: str,
    receiver: str,
    subject: str = "No subject",
    sender: str = "samiteshsharma667@gmail.com",
) -> str:
    """
    Send *html_body* to *receiver* via SendGrid.
    `sender` must be a verified address in your SendGrid account.
    """
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        message = Mail(from_email=sender,
                       to_emails=receiver,
                       subject=subject,
                       html_content=html_body)
        resp = sg.send(message)
        return f"✉️ Email sent (status {resp.status_code})"
    except Exception as e:
        return f"❌ SendGrid error: {e}"
