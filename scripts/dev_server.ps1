$env:PYTHONPATH = "$PWD"
uvicorn api.main:app --reload --port 8000
