import threading
import requests
import time
# import features.github.githubAccess as github

def startMcpServer():
    from  server import app
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

def main():
    try:
        server_thread = threading.Thread(target=startMcpServer, daemon=False)
        server_thread.start()
        time.sleep(1) 
        # response = requests.get("http://127.0.0.1:8000/functions")
        # print("Available functions:",response.json())
        while True:
            try:
                  time.sleep(1)
            except KeyboardInterrupt:
                print("\n Shuttind down server")
                break
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()