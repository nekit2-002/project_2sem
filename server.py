from flask import Flask, request, abort
from json import loads
app = Flask(__name__)

@app.route("/", methods=['POST'])
def index():
    try:
        payload = loads(request.data)
        print (payload["repository"]["name"])
        if request.headers.get('X-GitHub-Event') == "push":
            print ("%s push %d commits to %s" \
            % (payload["pusher"]["name"], len(payload["commits"]), payload["ref"]))
        # --&gt;
    except:
        abort(400)

    return "Ok!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4567)

#dkjifjifijfe