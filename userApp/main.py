from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from annoy.model_query import QueryModel
from annoy.pipline import pipline
import numpy as np
from typing import List
from MapReduceJob.mr_job import TopRankingSongs
from Models.models import User, Song, OLAPDatabase, UserSongHistory, db
import csv
import random
import pandas as pd

app = Flask(__name__)
app.secret_key = "UserAppSecretKey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)

qModel : QueryModel


# Routes
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session["user_id"] = user.id
        return redirect(url_for("dashboard"))
    else:
        return render_template("index.html", error="Invalid username or password.")


@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return render_template("index.html", error="Username already exists.")
    
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    session["user_id"] = new_user.id
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("home"))
    
    user = User.query.get(session["user_id"])
    listnedSongs = user.song_history
    top_ranking_songs = OLAPDatabase.query.all()
    return render_template("dashboard.html", username=user.username, songs=top_ranking_songs)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/play/<int:song_id>" , methods=["POST"])
def play_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return "Song not found", 404

    #increment song count by 1
    song.count += 1

    user_id = session.get("user_id")
    user_song_history = UserSongHistory.query.filter_by(user_id=user_id, song_id=song.id).first()
    user_song_history.is_favourite = request.form.get("is_favourite", "off") == "on"

    if user_song_history:
        user_song_history.play_count += 1
    else:
        user_song_history = UserSongHistory(id=user_id, song_id=song.id, play_count=1, start_time=datetime.now())
        db.session.add(user_song_history)

    db.session.commit()

    qVector = np.array([
        song.year, song.bpm, song.energy, song.danceability, song.dB, song.liveness,
        song.valence, song.duration, song.acousticness, song.speechiness, song.popularity
    ])

    recommendedSongs = recommendatation(qVector=qVector)

    recommendedSongsObj = []

    for rec in recommendedSongs:
        # rec[0] is [title, artist, top_genre]
        title, artist, top_genre = rec[0]
        song_obj = Song.query.filter_by(title=title, artist=artist, top_genre=top_genre).first()
        if song_obj:
            recommendedSongsObj.append(song_obj)
    
    return render_template("play.html", playingSong=song, recommendedSongs=recommendedSongsObj)


def recommendatation(qVector : np.ndarray) -> List[tuple]:
    return qModel.query.query_tree(q_vec=qVector, k=10)


# Init DB & Test Data
if __name__ == "__main__":
    with app.app_context(): 
        db.create_all()
        db.session.commit()
        
        mrjob = TopRankingSongs()
        songs = Song.query.all()

        mrjob.mapReduce(db, songs)

        app.run(debug=True)



