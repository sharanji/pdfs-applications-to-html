import sys

from flask import Flask
from flask_cors import CORS

sys.path.insert(0, "apis/")

from common.routes import all_routes 
from db import Base, engine

app = Flask(__name__, static_folder="static")
CORS(app)

def configure_app_routes():
    for route in all_routes:
        api_url = route[0]
        handler = route[1]
        methods = route[2]
        app.add_url_rule(
            api_url, "{}|{}".format(route, handler), handler, methods=methods
        )


configure_app_routes()


@app.route("/hello")
def hello_world():
    Base.metadata.create_all(engine)
    return "True"

@app.route("/", methods=["GET"])
def index():
    return {"msg": "Hello from Vercel + Flask"}


if __name__ == "__main__":
    app.run(port=3000,debug=True)
