from fastapi import FastAPI

app = FastAPI(title="Project Atlas API")

@app.get("/health")
def health_check():
    return {"status": "ok"}
