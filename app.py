import datetime
import requests
import os
from collections import OrderedDict

from flask import Flask, request, redirect, render_template # type: ignore

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/<name>/<repo>")
def redir(name, repo):
    return redirect("https://github.com/" + name + "/" + repo)

@app.route("/form")
def to_user():
    return redirect("/" + request.args.get("name") + "/")

@app.route("/<name>/")
def user(name):
    repos = []

    for page in range(1, 15):
        these = requests.get("https://api.github.com/users/" + name + "/repos", params={
            "per_page": 100,
            "page": page,
            "direction": "desc"
        }, headers={
            "User-Agent": "fiatjaf",
            "Authorization": "token " + os.getenv("GITHUB_TOKEN")
        }).json()
        if len(these) == 0:
            break
        repos += these

    groups = OrderedDict()
    for repo_object in repos:
        try:
            repo = {
                "name": repo_object["name"],
                "stars": repo_object["stargazers_count"]
            }
        except:
            print(repo_object)
            break
        prefix, *_ = repo["name"].split('-')
        group = groups.get(prefix) or []
        group.append(repo) if repo["name"] != prefix else group.insert(0, repo)
        groups[prefix] = group

    return render_template('userpage.html', name=name, groups=groups)

@app.after_request
def add_header(response):
    response.expires = datetime.datetime.now() + datetime.timedelta(minutes=60)
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
