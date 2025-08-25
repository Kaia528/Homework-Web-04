from flask import Flask, request, render_template, redirect
import socket, json
from datetime import datetime
from pathlib import Path
import threading

app = Flask(__name__, template_folder="templates", static_folder="static")

UDP_PORT = 5009
DATA_JSON = Path("storage/data.json")
DATA_JSON.parent.mkdir(exist_ok=True)

def append_message(username, message):
    if DATA_JSON.exists():
        db = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    else:
        db = {}
    key = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    db[key] = {"username": username, "message": message}
    DATA_JSON.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


def run_udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(("0.0.0.0", UDP_PORT))
        while True:
            data, addr = s.recvfrom(1024)
            try:
                payload = json.loads(data.decode("utf-8"))
                append_message(payload.get("username",""), payload.get("message",""))
            except Exception:
                pass


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/message", methods=["GET", "POST"])
def message():
    if request.method == "POST":
        username = request.form["username"]
        msg = request.form["message"]
        payload = {"username": username, "message": msg}

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(json.dumps(payload).encode("utf-8"), ("127.0.0.1", UDP_PORT))
        return redirect("/")
    return render_template("message.html")

if __name__ == "__main__":
    threading.Thread(target=run_udp_server, daemon=True).start()
    app.run(port=3000, debug=True, use_reloader=False)








