"""Instant API."""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from openai import OpenAI


app = FastAPI()


@app.get("/")
def root():
    """Instant API Root endpoint."""
    print("Instant API endpoint called.")
    return "It's Alive from production!"


@app.get("/welcome", response_class=HTMLResponse)
def welcome():
    """Instant API Welcome endpoint."""
    client = OpenAI()
    message = """
    You are on a website that has just been deployed to production for the first time!
    Please reply with an enthusiastic announcement to welcome visitors to the site,
    explaining that it is live on production for the first time!
    """
    messages = [{"role": "user", "content": message}]
    response = client.chat.completions.create(model="gpt-5.4-mini", messages=messages)
    reply = response.choices[0].message.content.replace("\n", "<br/>")
    html = f"""<html>
        <head>
            <title>Live in an Instant!</title>
            <meta name="color-scheme" content="light dark">
        </head>
        <body>
            <p>{reply}</p>
        </body></html>
    """
    return html
