import requests


class SearchBot:
    def __init__(self, api_key):
        self.key = api_key
        self.poster_path = 'https://image.tmdb.org/t/p/w500'

    def scour(self, movie_query):
        search = f'https://api.themoviedb.org/3/search/movie?api_key={self.key}&query={movie_query}'
        results = []

        response = requests.get(url=search)
        response.raise_for_status()

        data = response.json()

        for entry in data['results']:
            template = {
                'id': f"{entry['id']}",
                'title': f"{entry['title']}",
                'year': f"{entry['release_date']}",
                # 'description': f"{entry['overview']}",
                # 'poster': f"{self.poster_path}+{entry['poster_path']}",
            }

            results.append(template)

        return results

    def pinpoint(self, num):
        pin = f'http://api.themoviedb.org/3/movie/{num}?api_key={self.key}'

        response = requests.get(url=pin)
        response.raise_for_status()

        data = response.json()

        template = {
            'title': f"{data['title']}",
            'year': f"{data['release_date'].split('-')[0]}",
            'description': f"{data['overview']}",
            'poster': f"{self.poster_path}{data['poster_path']}",
        }

        return template


