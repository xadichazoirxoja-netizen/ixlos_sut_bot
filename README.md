services:
  - type: web
    name: ixlos-sut-bot
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
