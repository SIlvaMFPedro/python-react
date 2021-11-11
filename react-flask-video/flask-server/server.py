# -----------------------------
#   USAGE
# -----------------------------
# python server.py

# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from flask import Flask

# Construct the flask app
app = Flask(__name__)


# -----------------------------
#   API FUNCTIONS
# -----------------------------
# Members API route
@app.route("/members")
def members():
    return {"members": ["Member1", "Member2", "Member3", "Member4", "Member5"]}


# -----------------------------
#   MAIN
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
