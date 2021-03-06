# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_restx.representations import output_json
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()
    # director = fields.Str()
    # genre = fields.Str()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

api = Api(app)
api.representations = {'application/json; charset=utf-8': output_json}
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


@movies_ns.route('/')
class MovieView(Resource):
    def get(self):
        all_movie_genre_director = db.session.query(Movie.id,
                                                    Movie.title,
                                                    Movie.description,
                                                    Movie.trailer,
                                                    Movie.rating,
                                                    Genre.name.label('genre'),
                                                    Director.name.label('director')).join(Director).join(Genre)
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')

        if director_id:
            all_movie_genre_director = all_movie_genre_director.filter(Movie.director_id == director_id)

        if genre_id:
            all_movie_genre_director = all_movie_genre_director.filter(Movie.genre_id == genre_id)
        all_movie = all_movie_genre_director.all()
        return movies_schema.dump(all_movie)

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f"?????????? ?? id {new_movie.id} ????????????????"


@movies_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        try:
            movie = db.session.query(Movie).get(mid)
        except NameError:
            return "?????????? ???? ????????????", 404
        except AttributeError:
            return f"???????????? ?? id {mid} ?????? ?? ????????????", 404
        if movie:
            return movie_schema.dump(movie), 200
        return "?????? ???????????? ????????????"

    def put(self, mid):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return f"?????????? ?? id {mid} ???? ????????????", 404

        req_json = request.json
        movie.title = req_json['title']
        movie.description = req_json['description']
        movie.trailer = req_json['trailer']
        movie.year = req_json['year']
        movie.rating = req_json['rating']
        movie.genre_id = req_json['genre_id']
        movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f"Movie ?? id {mid} ????????????????", 204

    def patch(self, mid):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return f"?????????? ?? id {mid} ???? ????????????", 404

        req_json = request.json
        if 'title' in req_json:
            movie.title = req_json['title']
        if 'description' in req_json:
            movie.description = req_json['description']
        if 'trailer' in req_json:
            movie.trailer = req_json['trailer']
        if 'year' in req_json:
            movie.year = req_json['year']
        if 'rating' in req_json:
            movie.rating = req_json['rating']
        if 'genre_id' in req_json:
            movie.genre_id = req_json['genre_id']
        if 'director_id' in req_json:
            movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f"Movie ?? id {mid} ????????????????", 204

    def delete(self, mid):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return f"?????????? ?? id {mid} ???? ????????????", 404

        db.session.delete(movie)
        db.session.commit()
        return f"?????????? ?? id {mid} ????????????", 204


if __name__ == '__main__':
    app.run(debug=True)
