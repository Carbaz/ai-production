"""API for generating new business ideas for AI Agents using OpenAI's GPT-5 model."""

import os

from fastapi import Depends, FastAPI
from fastapi.responses import PlainTextResponse, StreamingResponse
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from openai import OpenAI


app = FastAPI()

clerk_config = ClerkConfig(
    jwks_url=os.getenv("CLERK_JWKS_URL"),
    verify_iat=False,
    leeway=30.0)
clerk_guard = ClerkHTTPBearer(clerk_config)


@app.get("/api/straight", response_class=PlainTextResponse)
def idea():
    """Endpoint to generate a new business idea for AI Agents, non-streaming."""
    client = OpenAI()
    message = "Come up with a new business idea for AI Agents"
    messages = [{"role": "user", "content": message}]
    response = client.chat.completions.create(model="gpt-5-nano", messages=messages)
    return response.choices[0].message.content


@app.get("/api")
def idea_stream(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    """Endpoint to stream a new business idea for AI Agents."""
    user_id = creds.decoded["sub"]  # User ID from JWT - available for future use
    # We now know which user is making the request!
    # You could use user_id to:
    # - Track usage per user
    # - Store generated ideas in a database
    # - Apply user-specific limits or customization

    client = OpenAI()
    message = """
    Reply with a new business idea for AI Agents,
    formatted with headings, sub-headings and bullet points
    """
    messages = [{"role": "user", "content": message}]
    stream = client.chat.completions.create(model="gpt-5-nano", messages=messages,
                                            stream=True)

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
