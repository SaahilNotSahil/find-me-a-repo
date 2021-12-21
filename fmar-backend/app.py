from flask import Flask, redirect, url_for, render_template
from flask_dance.contrib.github import make_github_blueprint, github
from decouple import config

import json

app = Flask(__name__)

bp = make_github_blueprint(client_id=config('CLIENT_ID'),
                           client_secret=config('CLIENT_SECRET'), scope='repo,user')
app.register_blueprint(bp, url_prefix='/')
app.secret_key = config('SECRET_KEY')

@app.route("/")
def login():
    global name
    global accInfoJSON

    if not github.authorized:
        return redirect(url_for("github.login"))
    accInfo = github.get("/user")

    if accInfo.ok:
        accInfoJSON = accInfo.json()
        username = accInfoJSON['login']
        f = open(f"acc_{username}.json", "w")
        f.write(json.dumps(accInfoJSON))
        f.close()

        return render_template("home.html", name=username, acc=accInfoJSON)
