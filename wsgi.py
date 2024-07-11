from fastapi import FastAPI
from app import app as flask_app

app = FastAPI()

@app.get("/fastapi")
async def read_root():
    return {"message": "Hello from FastAPI!"}

# Mount the Flask application
app.mount("/flask", flask_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
