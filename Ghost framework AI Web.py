## ghost framework AI 
import os
import json
import time
import random
import subprocess
from flask import Flask, request, jsonify, render_template_string
from threading import Thread

app = Flask(__name__)
history = []
log_file = "ghost_log.json"

HTML_UI = '''
<!doctype html>
<html>
  <head>
    <title>Ghost Framework AI Edition</title>
    <style>
      body { background: #1e1e1e; color: lime; font-family: monospace; padding: 20px; }
      input, button { padding: 10px; font-size: 16px; margin: 5px; background: black; color: lime; border: 1px solid lime; }
      textarea { width: 100%; height: 300px; background: black; color: lime; font-family: monospace; }
    </style>
  </head>
  <body>
    <h2>Ghost Framework AI Edition</h2>
    <input id="command" placeholder="Enter ADB command">
    <button onclick="send()">Send</button>
    <button onclick="suggest()">AI Suggest</button>
    <button onclick="save()">Save Log</button>
    <pre id="output"></pre>
    <script>
      function send() {
        const cmd = document.getElementById('command').value;
        fetch('/run', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command: cmd })
        })
        .then(res => res.json())
        .then(data => { document.getElementById('output').textContent += data.log + "\\n"; });
      }
      function suggest() {
        fetch('/suggest').then(res => res.json()).then(data => {
          document.getElementById('command').value = data.command;
          document.getElementById('output').textContent += "[AI Suggested] " + data.command + "\\n";
        });
      }
      function save() {
        fetch('/save').then(() => alert("Log saved!"));
      }
    </script>
  </body>
</html>
'''

def log_event(data):
    data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = json.dumps(data)
    with open(log_file, "a") as f:
        f.write(entry + "\n")
    return entry

@app.route('/')
def index():
    return render_template_string(HTML_UI)

@app.route('/run', methods=['POST'])
def run_command():
    data = request.get_json()
    cmd = data.get("command", "")
    history.append(cmd)
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10).decode()
        log = log_event({"event": "Run Command", "command": cmd, "output": output})
        return jsonify({"log": log})
    except subprocess.CalledProcessError as e:
        log = log_event({"event": "Command Error", "command": cmd, "output": e.output.decode()})
        return jsonify({"log": log})
    except subprocess.TimeoutExpired:
        log = log_event({"event": "Command Timeout", "command": cmd})
        return jsonify({"log": log})

@app.route('/suggest')
def suggest():
    common = [
        "adb devices",
        "adb shell pm list packages",
        "adb shell getprop",
        "adb shell input keyevent 26",
        "adb install myapp.apk",
        "adb logcat -d"
    ]
    if not history:
        suggestion = random.choice(common)
    elif "install" in history[-1]:
        suggestion = "adb shell monkey -p com.example -v 1"
    else:
        suggestion = random.choice(common)
    return jsonify({"command": suggestion})

@app.route('/save')
def save():
    os.rename(log_file, f"ghost_log_{int(time.time())}.json")
    return jsonify({"status": "saved"})

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Start server
if __name__ == "__main__":
    print("Open your browser to http://localhost:8080")
    Thread(target=run_flask).start()
