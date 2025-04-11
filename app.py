import threading
import requests
import time

def startMcpServer():
    from  server import app
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

def main():
    try:
        server_thread = threading.Thread(target=startMcpServer, daemon=True)
        server_thread.start()

        time.sleep(1) 
        # response = requests.get("http://127.0.0.1:8000/")
        # print("Available functions:",response.json())
    except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()