from flask import *
from os import environ
import requests

from ruqqus.__main__ import app

@app.route("/giphy", methods=["GET"])
@app.route("/giphy<path>", methods=["GET"])
def giphy():
    searchTerm = request.args.get("searchTerm", "")
    limit = int(request.args.get("limit", ""))
    if searchTerm and limit:
        url = f"https://api.giphy.com/v1/gifs/search?q={searchTerm}&api_key={environ.get('GIPHY_KEY')}&limit={limit}"
    elif searchTerm and not limit:
        url = f"https://api.giphy.com/v1/gifs/search?q={searchTerm}&api_key={environ.get('GIPHY_KEY')}&limit=48"
    else:
        url = f"https://api.giphy.com/v1/gifs?api_key={environ.get('GIPHY_KEY')}&limit=48"
    return jsonify(requests.get(url).json())
    
