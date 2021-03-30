from flask import Flask, request, abort
from json import loads
app = Flask(__name__)

@app.route("/", methods=['POST'])
def index():
    try:
        payload = loads(request.data)
        print(payload["repository"]["name"])
    except:
        abort(400)

    return "Ok!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4567)