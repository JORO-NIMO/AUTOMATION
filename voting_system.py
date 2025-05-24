import os
import time
from flask import Flask, redirect, url_for, request, session, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import RadioField, SubmitField

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "random_secret_key"

# CSRF Protection
csrf = CSRFProtect(app)

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

# Flask-WTF form for voting with CSRF
class VoteForm(FlaskForm):
    candidate = RadioField(
        "Select Candidate",
        choices=[("Candidate A", "Candidate A"), ("Candidate B", "Candidate B")],
        default="Candidate A"
    )
    submit = SubmitField("Submit Vote")

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

    form = VoteForm()
    if form.validate_on_submit():
        candidate = form.candidate.data
        email = session["email"]

        existing_vote = Vote.query.filter_by(email=email).first()
        if existing_vote:
            return "You have already voted."

        new_vote = Vote(email=email, candidate=candidate)
        db.session.add(new_vote)
        db.session.commit()

        return "Vote submitted successfully!"

    # Render the voting form with CSRF protection
    return render_template_string('''
        <form method="post">
            {{ form.hidden_tag() }}
            {{ form.candidate.label }}<br>
            {% for subfield in form.candidate %}
                {{ subfield() }} {{ subfield.label }}<br>
            {% endfor %}
            {{ form.submit() }}
        </form>
    ''', form=form)

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
