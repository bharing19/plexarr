from configparser import ConfigParser
from urllib.parse import urljoin
from datetime import datetime as dt
import pyombi
import os

class OmbiAPI():
    """Wrapper for TMDB API via tmdbsimple

    """
    def __init__(self):
        """Constructor requires Ombi info

        From config:
            api_key (str): API key.
        """
        config = ConfigParser()
        config.read(os.path.join(os.path.expanduser('~'), '.config', 'plexarr.ini'))

        self.ombi = pyombi.Ombi(
            ssl=config['ombi'].get('ssl'),
            host=config['ombi'].get('host'),
            port=config['ombi'].get('port'),
            urlbase=config['ombi'].get('urlbase'),
            username=config['ombi'].get('username'),
            password=config['ombi'].get('password'),
            api_key=config['ombi'].get('api_key')
        )
        self.ombi.authenticate()

    def request(self, path, data=None):
        import requests

        url = urljoin(self.ombi._base_url, path.strip('/'))
        headers = {
            "UserName": self.ombi._username,
            "ApiKey": self.ombi._api_key
        }

        if not data:
            res = requests.get(url=url, headers=headers, timeout=10)
        else:
            res = requests.post(url=url, headers=headers, json=data, timeout=10)
        return res

    def getMovieRequests(self):
        path = '/Request/movie'
        return self.request(path=path).json()

    def getMovies(self):
        """Get all movies that have been requested by not yet downloaded

        Returns:
            JSON Array
        """
        return [m for m in self.ombi.get_movie_requests() if not m.get('available')]

    def getAllMovies(self):
        """Get all movies that have been requested

        Returns:
            JSON Array
        """
        return self.ombi.get_movie_requests()

    def searchMovie(self, query='', year=None):
        """Search for a Movie

        Args:
            Required - query (str) - Movie title to search for
            Optional - year (int) - Movie released year to apply as a filter
        Returns:
            JSON Array
        """
        if not year:
            return self.ombi.search_movie(query=query)
        return [m for m in self.ombi.search_movie(query=query) if dt.fromisoformat(m.get('releaseDate')).year == year]
