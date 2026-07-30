"""API for generating new business ideas for AI Agents using OpenAI's GPT-5 model."""

import os
from logging import getLogger

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from openai import OpenAI


_logger = getLogger(__name__)

app = FastAPI()
_logger.info("Starting API.")

clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)
_logger.info("Clerk configuration set up.")


@app.get("/api")
def idea(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    """Endpoint to stream a new business idea for AI Agents."""
    _logger.info("Generating a new business idea for AI Agents (streaming).")
    user_id = creds.decoded["sub"]  # User ID from JWT - available for future use
    # We now know which user is making the request!
    # You could use user_id to:
    # - Track usage per user
    # - Store generated ideas in a database
    # - Apply user-specific limits or customization
    _logger.info(f"Request made by user: {user_id}")
    client = OpenAI()
    message = """
    Reply with a new business idea for AI Agents,
    formatted with headings, sub-headings and bullet points
    """
    messages = [{"role": "user", "content": message}]
    _logger.info("Sending request to OpenAI GPT-5 model.")
    stream = client.chat.completions.create(model="gpt-5-nano", messages=messages,
                                            stream=True)
    _logger.info("Streaming response from OpenAI GPT-5 model.")

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"

    _logger.info("Returning streaming response to client.")
    return StreamingResponse(event_stream(), media_type="text/event-stream")
