from fastapi import FastAPI

app = FastAPI(title="Advance Web Scraper")

@app.get("/")
def read_root():
    return {"message": "Welcome to Advance Web Scraper API"}
