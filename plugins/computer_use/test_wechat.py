import sys
import os
import json
import subprocess

def run_test():
    cmd = ["uv", "run", "src/main.py"]
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "computer",
            "arguments": {
                "action": "send_message_to",
                "app": "微信",
                "contact_name": "刘园园",
                "message": "你好，小主！   这是来自老李的 ai 发送的测试消息！"
            }
        }
    }
    
    print(f"Sending request: {json.dumps(req)}")
    
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    out, err = proc.communicate(input=json.dumps(req) + "\n")
    print("STDOUT:")
    print(out)
    print("STDERR:")
    print(err)

if __name__ == "__main__":
    run_test()
