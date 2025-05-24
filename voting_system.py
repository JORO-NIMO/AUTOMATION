pip install Flask Flask-OAuthlib Flask-SQLAlchemy requests

import os
import time
from flask import Flask, redirect, url_for, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.secret_key = "random_secret_key"

# Google OAuth Configuration
app.config["GOOGLE_CLIENT_ID"] = "YOUR_GOOGLE_CLIENT_ID"
app.config["GOOGLE_CLIENT_SECRET"] = "YOUR_GOOGLE_CLIENT_SECRET"
oauth = OAuth(app)
google = oauth.remote_app(
    "google",
    consumer_key=app.config["GOOGLE_CLIENT_ID"],
    consumer_secret=app.config["GOOGLE_CLIENT_SECRET"],
    request_token_params={"scope": "email"},
    base_url="https://www.googleapis.com/oauth2/v1/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///votes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    candidate = db.Column(db.String(50), nullable=False)

# Voting Window (Adjust as needed)
VOTING_START_TIME = time.time()
VOTING_DURATION = 24 * 60 * 60  # 24 hours in seconds

@app.route("/")
def home():
    return '<a href="/login">Login with Google to Vote</a>'

@app.route("/login")
def login():
    return google.authorize(callback=url_for("authorized", _external=True))

@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("home"))

@app.route("/login/authorized")
def authorized():
    resp = google.authorized_response()
    if resp is None or resp.get("access_token") is None:
        return "Access Denied."

    session["google_token"] = (resp["access_token"], "")
    user_info = google.get("userinfo")
    email = user_info.data["email"]

    if not email.endswith("@std.must.ac.ug"):
        return "Unauthorized: Must use an official university email."

    session["email"] = email
    return redirect(url_for("vote"))

@app.route("/vote", methods=["GET", "POST"])
def vote():
    if "email" not in session:
        return redirect(url_for("home"))

    if time.time() > VOTING_START_TIME + VOTING_DURATION:
        return "Voting has ended."

    if request.method == "POST":
        candidate = request.form.get("candidate")
        email = session["email"]

        existing_vote = Vote.query.filter_by(email=email).first()
        if existing_vote:
            return "You have already voted."

        new_vote = Vote(email=email, candidate=candidate)
        db.session.add(new_vote)
        db.session.commit()

        return "Vote submitted successfully!"

    return """
    <form method="post">
        <label>Select Candidate:</label><br>
        <input type="radio" name="candidate" value="Candidate A"> Candidate A<br>
        <input type="radio" name="candidate" value="Candidate B"> Candidate B<br>
        <button type="submit">Submit Vote</button>
    </form>
    """

@app.route("/results")
def results():
    votes = Vote.query.all()
    results_data = {}
    for vote in votes:
        results_data[vote.candidate] = results_data.get(vote.candidate, 0) + 1
    return jsonify(results_data)

@google.tokengetter
def get_google_oauth_token():
    return session.get("google_token")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)