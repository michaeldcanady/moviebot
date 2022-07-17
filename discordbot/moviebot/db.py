import logging
from sqlalchemy import create_engine, MetaData, Table, Column, String, Boolean
import random
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

class MovieDb:
    """
    UserDb provides a set of helper functions over SQLAlchemy
    to handle db operations for userservice
    """

    def __init__(self, uri, logger=logging):
        self.engine = create_engine(uri)
        self.logger = logger
        self.movies_table = Table(
            'movies',
            MetaData(self.engine),
            Column('movieid', String, primary_key=True),
            Column('moviename', String, unique=True, nullable=False),
            Column('watched', Boolean, nullable=False)
        )

        # Set up tracing autoinstrumentation for sqlalchemy
        #SQLAlchemyInstrumentor().instrument(
        #    engine=self.engine,
        #    service='movies',
        #)
    
    def add_movie(self, movie):
        """Add a user to the database.
        Params: user - a key/value dict of attributes describing a new user
                    {'email': email, 'password': password, ...}
        Raises: SQLAlchemyError if there was an issue with the database
        """
        statement = self.movies_table.insert().values(movie)
        self.logger.debug('QUERY: %s', str(statement))
        with self.engine.connect() as conn:
            conn.execute(statement)
    
    def generate_movieid(self) -> str:
        """Generates a globally unique alphanumerical movieid."""
        self.logger.debug('Generating an movie ID')
        movieid = None
        with self.engine.connect() as conn:
            while movieid is None:
                movieid = str(random.randint(1e9, (1e10 - 1)))

                statement = self.movies_table.select().where(
                    self.movies_table.c.movieid == movieid
                )
                self.logger.debug('QUERY: %s', str(statement))
                result = conn.execute(statement).first()
                # If there already exists an movie, try again.
                if result is not None:
                    movieid = None
                    self.logger.debug(
                        'RESULT: movie ID already exists. Trying again')
        self.logger.debug('RESULT: movie ID generated.')
        return movieid

    def get_movie(self, movieid):
        """Get user data for the specified email.
        Params: email - the email of the user
        Return: a key/value dict of user attributes,
                {'email': email, 'userid': userid, ...}
                or None if that user does not exist
        Raises: SQLAlchemyError if there was an issue with the database
        """
        statement = self.movies_table.select().where(
            self.movies_table.c.movieid == movieid)
        self.logger.debug('QUERY: %s', str(statement))
        with self.engine.connect() as conn:
            result = conn.execute(statement).first()
        self.logger.debug('RESULT: fetched movie data for %s', movieid)
        return dict(result) if result is not None else None