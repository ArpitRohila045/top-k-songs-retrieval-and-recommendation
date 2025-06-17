from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime

db = SQLAlchemy()

class UserSongHistory(db.Model):
    __tablename__ = "user_song_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey("songs.id"), nullable=False)
    
    play_count = db.Column(db.Integer, default=0)
    start_time = db.Column(db.DateTime)
    is_favourite = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="song_history")
    song = db.relationship("Song", back_populates="user_history")




# Update your User and Song models like this:
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    song_history = db.relationship("UserSongHistory", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Song(db.Model):
    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    top_genre = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    bpm = db.Column(db.Integer, nullable=False)
    energy = db.Column(db.Float, nullable=False)
    danceability = db.Column(db.Float, nullable=False)
    dB = db.Column(db.Float, nullable=False)
    liveness = db.Column(db.Float, nullable=False)
    valence = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    acousticness = db.Column(db.Float, nullable=False)
    speechiness = db.Column(db.Float, nullable=False)
    popularity = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, default=0)

    user_history = db.relationship("UserSongHistory", back_populates="song", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Song {self.title} by {self.artist} ({self.year})>"


class OLAPDatabase(db.Model):
    __tablename__ = "olap_database"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    artist = db.Column(db.String(100), nullable=False)
    top_genre = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    bpm = db.Column(db.Integer, nullable=False)
    energy = db.Column(db.Float, nullable=False)
    danceability = db.Column(db.Float, nullable=False)
    dB = db.Column(db.Float, nullable=False)
    liveness = db.Column(db.Float, nullable=False)
    valence = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    acousticness = db.Column(db.Float, nullable=False)
    speechiness = db.Column(db.Float, nullable=False)
    popularity = db.Column(db.Integer, nullable=False)
    count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Song {self.title} by {self.artist} ({self.year})>"