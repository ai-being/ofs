from flask import Flask, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "supersekrit"
blueprint = make_google_blueprint(
    client_id="1024809645050-v8af191r7qjf54pqa5g5bp49e1ld4bs0.apps.googleusercontent.com",
    client_secret="zKCr08jKz4TfRbnJ4O_KTDqn",
    scope=["profile", "email"]
    
)
app.register_blueprint(blueprint, url_prefix="/google_api")

@app.route("/")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/plus/v1/people/me")
    print('resp')
    assert resp.ok, resp.text
    return "<h1>You are {email} on Google</h1>".format(email=resp.json()["emails"][0]["value"])

if __name__ == "__main__":
    app.run(debug=True)