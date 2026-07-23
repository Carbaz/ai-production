"""API for generating new business ideas for AI Agents using OpenAI's GPT-5 model."""

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, StreamingResponse
from openai import OpenAI


app = FastAPI()


@app.get("/api/straight", response_class=PlainTextResponse)
def idea():
    """Endpoint to generate a new business idea for AI Agents, non-streaming."""
    client = OpenAI()
    message = "Come up with a new business idea for AI Agents"
    messages = [{"role": "user", "content": message}]
    response = client.chat.completions.create(model="gpt-5-nano", messages=messages)
    return response.choices[0].message.content


@app.get("/api")
def idea_stream():
    """Endpoint to stream a new business idea for AI Agents."""
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
                for line in lines:
                    yield f"data: {line}\n"
                yield "\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
