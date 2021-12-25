from flask import Flask, redirect, url_for, render_template, request, make_response
from flask_dance.contrib.github import make_github_blueprint, github
from decouple import config
from model import Model
import json

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

bp = make_github_blueprint(client_id=config('CLIENT_ID'),
                           client_secret=config('CLIENT_SECRET'), scope='repo,user')
app.register_blueprint(bp, url_prefix='/')
app.secret_key = config('SECRET_KEY')

username = ""
output = {}

def index():
    return render_template('index.html')

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/")
def login():
    global username

    if not github.authorized:
        return redirect(url_for("github.login"))
    accInfo = github.get("/user")

    if accInfo.ok:
        accInfoJSON = accInfo.json()
        username = accInfoJSON['login']
        f = open(f"acc_{username}.json", "w")
        f.write(json.dumps(accInfoJSON))
        f.close()

        return render_template("home.html", name=username)


@app.route("/input", methods=["POST", "OPTIONS"])
def input():
    global output

    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    else:
        data = request.json

        if data['pl'] == "any" and data['desc'] == "":
            return _corsify_actual_response(make_response({"alert": "yes"}))

        model = Model(data)
        model.createData()
        model.createModel()
        output = model.recommend()

        return _corsify_actual_response(make_response(output))

@app.route("/recoms")
def recoms():
    return render_template("repos.html", repo=json.loads(output), name=username)
