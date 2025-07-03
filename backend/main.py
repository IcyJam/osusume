import uvicorn


if __name__ == "__main__":
    print("running main...")
    uvicorn.run("app.api.routes:app", host="0.0.0.0", port=8000, reload=True)