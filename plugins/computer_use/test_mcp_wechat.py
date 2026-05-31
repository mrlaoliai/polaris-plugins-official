import sys
import json
import subprocess
import time

def read_message(proc):
    line = proc.stdout.readline()
    if not line:
        return None
    return json.loads(line)

def send_message(proc, msg):
    print(f"Sending: {json.dumps(msg, ensure_ascii=False)}")
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()

def run_test():
    cmd = ["uv", "run", "src/main.py"]
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 1. initialize
    req_init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    send_message(proc, req_init)
    res_init = read_message(proc)
    print(f"Received: {json.dumps(res_init, ensure_ascii=False)}")

    # 2. notifications/initialized
    notif_init = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    send_message(proc, notif_init)

    # 3. tools/call
    req_call = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "computer",
            "arguments": {
                "action": "send_message_to",
                "app": "wechat",
                "contact_name": "葛文强",
                "message": "这是来自老李的ai 发送的消息。"
            }
        }
    }
    send_message(proc, req_call)
    
    # Read the final result
    while True:
        res_call = read_message(proc)
        if res_call is None:
            break
        print(f"Received: {json.dumps(res_call, ensure_ascii=False)}")
        if res_call.get("id") == 2:
            break

    # Clean up
    proc.terminate()
    stdout, stderr = proc.communicate()
    if stderr:
        print(f"STDERR: {stderr}")

if __name__ == "__main__":
    run_test()
