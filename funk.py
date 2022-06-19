from app import *


def get_name_genre_and_director():
    return db.session.query(Movie.id,
                            Movie.title,
                            Movie.description,
                            Movie.trailer,
                            Movie.rating,
                            Genre.name.label('genre'),
                            Director.name.label('director')).join(Director).join(Genre)
