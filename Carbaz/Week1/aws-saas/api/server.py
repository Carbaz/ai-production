"""API for generating new business ideas for AI Agents using OpenAI's GPT-5 model."""

import os
from logging import getLogger
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from openai import OpenAI
from pydantic import BaseModel


_logger = getLogger(__name__)

_logger.info("Starting API.")
app = FastAPI()

# Add CORS middleware (allows frontend to call backend)
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

# Clerk authentication setup
_logger.info("Setting up Clerk configuration.")
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)
_logger.info("Clerk configuration set up.")


# Defining the Pydantic model for the visit data.
class Visit(BaseModel):
    """Model representing a patient's visit data."""
    patient_name: str
    date_of_visit: str
    notes: str


SYSTEM_PROMPT = """
You are provided with notes written by a doctor from a patient's visit.
Your job is to summarize the visit for the doctor and provide an email.
Reply with exactly three sections with the headings:
### Summary of visit for the doctor's records
### Next steps for the doctor
### Draft of email to patient in patient-friendly language
"""


# Prompt generation function to create a user prompt based on the visit data.
def user_prompt_for(visit: Visit) -> str:
    """Generate a user prompt based on the visit data."""
    return f"""Create the summary, next steps and draft email for:
    Patient Name: {visit.patient_name}
    Date of Visit: {visit.date_of_visit}
    Notes:
    {visit.notes}
    """


# Streaming function to yield chunks of text from the Model's response.
def event_stream(stream):
    """Stream chunks of text from the Model's response."""
    for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            lines = text.split("\n")
            for line in lines[:-1]:
                yield f"data: {line}\n\n"
                yield "data:  \n"
            yield f"data: {lines[-1]}\n\n"


def access_denied_stream():
    """Stream error messages."""
    yield "data: Premium subscription required.\n\n"
    yield "data:  \n"


@app.post("/api/consultation")
def consultation_summary(visit: Visit,
                         creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    """Endpoint to stream a summary of a patient's visit based on doctor's notes."""
    _logger.info("Generating a summary of a patient's visit.")

    # Extracting user information from JWT token.
    user_id = creds.decoded["sub"]
    sub_plan = creds.decoded.get("pla", "free")
    _logger.info(f"Request made by user: {user_id} with subscription plan: {sub_plan}")

    if sub_plan != "u:premium_subscription":
        _logger.warning(f"Subscription plan does not have access to this feature.")
        # raise HTTPException(status_code=403, detail="Premium subscription required.")
        return StreamingResponse(access_denied_stream(), media_type="text/event-stream")

    # Preparing request for OpenAI model.
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt_for(visit)}]

    # Requesting a streaming response from the OpenAI model.
    _logger.info("Sending request to OpenAI model for consultation summary.")
    stream = OpenAI().chat.completions.create(model="gpt-5-nano", messages=messages,
                                              stream=True)

    # Streaming the response back to the client.
    _logger.info("Returning streaming response to client.")
    return StreamingResponse(event_stream(stream), media_type="text/event-stream")


@app.get("/health")
def health_check():
    """Health check endpoint (used for local Docker; Lambda does not invoke it)."""
    return {"status": "healthy"}


# Serve static files (our Next.js export) - MUST BE LAST!
static_path = Path("static")
if static_path.exists():
    @app.get("/")
    async def serve_root():
        """Serve the index.html file for the root path."""
        return FileResponse(static_path / "index.html")

    app.mount("/", StaticFiles(directory="static", html=True), name="static")
