from pypdf import PdfReader
import json

# Read profile PDF
try:
    reader = PdfReader("./data/profile.pdf")
    profile = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            profile += text
except FileNotFoundError:
    profile = "Profile not available"

# Read other data files
with open("./data/summary.md", "r", encoding="utf-8") as f:
    summary = f.read()

with open("./data/style.txt", "r", encoding="utf-8") as f:
    style = f.read()

with open("./data/facts.json", "r", encoding="utf-8") as f:
    facts = json.load(f)
