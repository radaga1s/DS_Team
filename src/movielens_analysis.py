import sys
from collections import Counter, namedtuple
import re
import os
import pytest
import requests
import json
from bs4 import BeautifulSoup as soup
from datetime import datetime as dt


class Movies:
    """
    Analyzing data from movies.csv
    """
    def __init__(self, path_to_the_file):
        self.filepath = path_to_the_file
        self.data = self.__read_file(path_to_the_file)

    def dist_by_release(self):
        """
        The method returns a dict or an OrderedDict where the keys are years and the values are counts.
        You need to extract years from the titles. Sort it by counts descendingly.
        """
        lst_of_years = [film[1][1] for film in self.data]
        release_years = dict(sorted(Counter(lst_of_years).items(), key=lambda x: x[1], reverse=True))

        return release_years

    def dist_by_genres(self):
        """
        The method returns a dict where the keys are genres and the values are counts.
        Sort it by counts descendingly.
        """
        lst_genres = [genre for sublist in self.data for genre in sublist[2]]
        genres = dict(sorted(Counter(lst_genres).items(), key=lambda x: x[1], reverse=True))
        return genres

    def most_genres(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the number of genres of the movie. Sort it by numbers descendingly.
        """
        genres_count_dict = {film[1][0]: len(film[2]) for film in self.data}
        movies = dict(Counter(genres_count_dict).most_common(n))
        return movies


    def __read_file(self, filepath):
        """
        Auxiliary function
        """
        try:
            if not os.path.isfile(filepath):
                raise Exception(f"File '{filepath}' does not exist")
            if 'movies.csv' in filepath:
                with open(filepath, mode='r', encoding='utf-8') as f:
                    pattern = r',(?=(?:[^"]*"[^"]*")*[^"]*$)'
                    pattern_film = r'"?(.*?)"?\s*\((\d{4})\)'
                    next(f)
                    lst = list()
                    for line in f:
                        line = re.split(pattern, line.strip())
                        lst.append(line)

                    for film in lst:
                        match = re.match(pattern_film, film[1])
                        film[1] = [str(match.group(1).strip()), int(match.group(2))]
                        film[2] = film[2].split('|')
                return lst
            else:
                raise Exception("Wrong file for this Class")

        except Exception as e:
            print(e)
            sys.exit(1)


class Tags:
    """
    Analyzing data from tags.csv
    """
    def __init__(self, path_to_the_file):
        self.filepath = path_to_the_file
        self.data = self.__read_file(path_to_the_file)

    def most_words(self, n):
        """
        The method returns top-n tags with most words inside. It is a dict
        where the keys are tags and the values are the number of words inside the tag.
        Drop the duplicates. Sort it by numbers descendingly.
        """
        all_tags = {row[2]: len(row[2].split()) for row in self.data}
        big_tags = sorted(all_tags.items(), key=lambda x: (-x[1], x[0]))[:n]
        return dict(big_tags)

    def longest(self, n):
        """
        The method returns top-n longest tags in terms of the number of characters.
        It is a list of the tags. Drop the duplicates. Sort it by numbers descendingly.
        """
        lst_of_tags = list({tag[2] for tag in self.data})
        big_tags = sorted(lst_of_tags, key=lambda x: (-len(x), x))
        return big_tags[:n]

    def most_words_and_longest(self, n):
        """
        The method returns the intersection between top-n tags with most words inside and
        top-n longest tags in terms of the number of characters.
        Drop the duplicates. It is a list of the tags.
        """
        top_words = list(self.most_words(n).keys())
        top_symbols = self.longest(n)
        big_tags = list(set(top_words) & set(top_symbols))
        return big_tags

    def most_popular(self, n):
        """
        The method returns the most popular tags.
        It is a dict where the keys are tags and the values are the counts.
        Drop the duplicates. Sort it by counts descendingly.
        """
        all_tags = [tag[2] for tag in self.data]
        popular_tags = dict(Counter(all_tags).most_common(n))

        return popular_tags

    def tags_with(self, word):
        """
        The method returns all unique tags that include the word given as the argument.
        Drop the duplicates. It is a list of the tags. Sort it by tag names alphabetically.
        """
        pattern = re.compile(r'\b' + re.escape(word.upper()) + r'\b')
        tags_with_word = sorted(list({tag[2] for tag in self.data if pattern.search(tag[2])}))
        if len(tags_with_word) > 0:
            return tags_with_word
        else:
            return None

    def __read_file(self, filepath):
        """
        This function reads a csv file and converts tags to a single capital letter format.
        """
        try:

            if not os.path.isfile(filepath):
                raise Exception(f"File '{filepath}' does not exist")
            if 'tags.csv' in filepath:
                with open(filepath, mode='r', encoding='utf-8') as f:
                    next(f)
                    lst = [row.strip().replace('\n', '').replace('"', '').split(',') for row in f.readlines()]
                    for row in lst:
                        row[2] = row[2].upper()
                    return lst
            else:
                raise Exception("Wrong file for this Class")
        except Exception as e:
            print(e)
            sys.exit(1)


class Ratings:
    """
    Analyzing data from ratings.csv
    """
    RatingData = namedtuple('RatingData', ['user_id', 'movie_id', 'rating', 'date',
                                           'title', 'release', 'genre'])

    def __init__(self, path_to_the_file='../datasets/ratings.csv'):
        try:
            if path_to_the_file != '../datasets/ratings.csv':
                raise Exception("Wrong file for this Class")
            else:
                self.movies_file = '../datasets/movies.csv'
                self.ratings_file = path_to_the_file
                self.ratings_data, key_cnt = {}, 0
                with open(self.ratings_file, 'r', encoding='utf8') as ratings_f, open(self.movies_file, 'r',
                                                                                      encoding='utf8') as movies_f:
                    next(ratings_f), next(movies_f)
                    for movie_line in movies_f:
                        if '\"' in movie_line:
                            movie_id, *title_year, genre = movie_line.strip().split(',')
                            string = ','.join(title_year).strip('\"')
                            title, release = string[:-7], string[-5:-1]
                        else:
                            movie_id, title_year, genre = movie_line.strip().split(',')
                            title, release = title_year[:-7], title_year[-5:-1]
                        for user_line in ratings_f:
                            user_id, u_movie_id, rating, date = user_line.strip().split(',')
                            if movie_id == u_movie_id:
                                key_cnt += 1
                                data_line = Ratings.RatingData(user_id, movie_id, rating, date, title, release, genre)
                                self.ratings_data.update({key_cnt: data_line})
                            else:
                                break
        except Exception as e:
            print(e)
            sys.exit(1)

    class Movies:
        def __init__(self, path_to_the_file='../datasets/ratings.csv'):
            Ratings.__init__(self, path_to_the_file)

        def dist_by_year(self):
            """
            The method returns a dict where the keys are years and the values are counts.
            Sort it by years ascendingly. You need to extract years from timestamps.
            """
            ratings_by_year = {}
            for line in self.ratings_data.values():
                year = dt.fromtimestamp(int(line.date)).year
                ratings_by_year[year] = ratings_by_year.get(year, 0) + 1
            ratings_by_year = {k: v for k, v in sorted(ratings_by_year.items(), key=lambda x: int(x[0]))}
            return ratings_by_year

        def dist_by_rating(self):
            """
            The method returns a dict where the keys are ratings and the values are counts.
            Sort it by ratings ascendingly.
            """
            ratings_distribution = {}
            for line in self.ratings_data.values():
                mark = line.rating
                ratings_distribution[mark] = ratings_distribution.get(mark, 0) + 1
            ratings_distribution = {float(k): v for k, v in sorted(ratings_distribution.items(), key=lambda x: float(x[0]))}
            return ratings_distribution

        def top_by_num_of_ratings(self, n):
            """
            The method returns top-n movies by the number of ratings.
            It is a dict where the keys are movie titles and the values are numbers.
            Sort it by numbers descendingly.
            """
            top_movies = {}
            for line in self.ratings_data.values():
                title = line.title
                top_movies[title] = top_movies.get(title, 0) + 1
            top_movies = {k: v for k, v in sorted(top_movies.items(), key=lambda x: x[1], reverse=True)[:n]}
            return top_movies

        def top_by_ratings(self, n, metric='average'):
            """
            The method returns top-n movies by the average or median of the ratings.
            It is a dict where the keys are movie titles and the values are metric values.
            Sort it by metric descendingly.
            The values should be rounded to 2 decimals.
            """
            top_movies, d = {}, {}
            for line in self.ratings_data.values():
                title, mark = line.title, float(line.rating)
                d.setdefault(title, []).append(mark)
            d = {k: sorted(v) for k, v in d.items() if len(v) >= 5}
            if metric == 'average':
                for title, marks_list in d.items():
                    top_movies[title] = float(f'{sum(marks_list) / len(marks_list):.2f}')
            elif metric == 'median':
                for title, marks_list in d.items():
                    length = len(marks_list)
                    if length % 2:
                        median = marks_list[length // 2]
                    else:
                        median = (marks_list[length // 2 - 1] + marks_list[length // 2]) / 2
                    top_movies[title] = float(f'{median:.2f}')
            top_movies = {k: v for k, v in sorted(top_movies.items(), key=lambda x: x[1], reverse=True)[:n]}
            return top_movies

        def top_controversial(self, n):
            """"
            The method returns top-n movies by the variance of the ratings.
            It is a dict where the keys are movie titles and the values are the variances.
            Sort it by variance descendingly.
            The values should be rounded to 2 decimals.
            """
            top_movies, d = {}, {}
            for line in self.ratings_data.values():
                title, mark = line.title, float(line.rating)
                d.setdefault(title, []).append(mark)
            d = {k: v for k, v in d.items() if len(v) >= 5}
            for title, marks_list in d.items():
                mean = sum(marks_list) / len(marks_list)
                variance = float(f'{sum((i - mean) ** 2 for i in marks_list) / len(marks_list):.2f}')
                top_movies[title] = variance
            top_movies = {k: v for k, v in sorted(top_movies.items(), key=lambda x: x[1], reverse=True)[:n]}
            return top_movies

    class Users(Movies):
        def user_activity(self):
            """
            This method returns the distribution of users by the number of ratings made by them.
            """
            d, result = Counter(line.user_id for line in self.ratings_data.values()), {}
            for marks_amount in d.values():
                if marks_amount == 1:
                    result['1 mark'] = result.get('1 mark', 0) + 1
                elif marks_amount in range(2, 6):
                    result['2-5 marks'] = result.get('2-5 marks', 0) + 1
                elif marks_amount in range(6, 10):
                    result['6-9 marks'] = result.get('6-9 marks', 0) + 1
                elif marks_amount in range(10, 20):
                    result['10-19 marks'] = result.get('10-19 marks', 0) + 1
                elif marks_amount in range(20, 50):
                    result['20-49 marks'] = result.get('20-49 marks', 0) + 1
                elif marks_amount in range(50, 100):
                    result['50-99 marks'] = result.get('50-99 marks', 0) + 1
                elif marks_amount in range(100, 250):
                    result['100-249 marks'] = result.get('100-249 marks', 0) + 1
                elif marks_amount in range(250, 500):
                    result['250-499 marks'] = result.get('250-499 marks', 0) + 1
                elif marks_amount >= 500:
                    result['500+ marks'] = result.get('500+ marks', 0) + 1
            return {k: v for k, v in sorted(result.items(), key=lambda x: x[1], reverse=True)}

        def user_tendency(self, metric='average'):
            """
            This method returns the distribution of users by average or median ratings made by them.
            """
            d, result = {}, {}
            for line in self.ratings_data.values():
                user, mark = line.user_id, float(line.rating)
                d.setdefault(user, []).append(mark)
            d = {k: sorted(v) for k, v in d.items() if len(v) >= 5}
            if metric == 'average':
                for user, marks_list in d.items():
                    d[user] = float(f'{sum(marks_list) / len(marks_list):.2f}')
            elif metric == 'median':
                for user, marks_list in d.items():
                    length = len(marks_list)
                    if length % 2:
                        median = marks_list[length // 2]
                    else:
                        median = (marks_list[length // 2 - 1] + marks_list[length // 2]) / 2
                    d[user] = float(f'{median:.2f}')
            for mark in d.values():
                if mark < 1:
                    result['0.5-1.0 marks'] = result.get('0.5-1.0 marks', 0) + 1
                elif 1 <= mark < 2:
                    result['1.0-1.99 marks'] = result.get('1.0-1.99 marks', 0) + 1
                elif 2 <= mark < 3:
                    result['2.0-2.99 marks'] = result.get('2.0-2.99 marks', 0) + 1
                elif 3 <= mark < 4:
                    result['3.0-3.99 marks'] = result.get('3.0-3.99 marks', 0) + 1
                elif 4 <= mark < 4.5:
                    result['4.0-4.49 marks'] = result.get('4.0-4.49 marks', 0) + 1
                elif mark >= 4.5:
                    result['4.5-5.0 marks'] = result.get('4.5-5.0 marks', 0) + 1
                else:
                    result['WASTED DATA'] = result.get('WASTED DATA', 0) + 1
            return {k: v for k, v in sorted(result.items(), key=lambda x: x[1], reverse=True)}

        def user_controversial(self, n):
            """
            This method returns top-n users with the biggest variance of their ratings.
            """
            result, d = {}, {}
            for line in self.ratings_data.values():
                user, mark = line.user_id, float(line.rating)
                d.setdefault(user, []).append(mark)
            d = {k: v for k, v in d.items() if len(v) >= 5}
            for user, marks_list in d.items():
                mean = sum(marks_list) / len(marks_list)
                variance = float(f'{sum((i - mean) ** 2 for i in marks_list) / len(marks_list):.2f}')
                result[user] = variance
            result = {k: v for k, v in sorted(result.items(), key=lambda x: x[1], reverse=True)[:n]}
            return result


class Links:
    """
    Analyzing data from links.csv
    """
    FilmData = namedtuple('FilmData', ['movie_id', 'imdb_id', 'title', 'genre',
                                       'age_rating', 'release', 'runtime',
                                       'imdb_rating', 'meta_rating', 'director',
                                       'starring', 'wwgross', 'budget', 'plot'])
    data_map = {'movieID': 'movie_id', 'imdbID': 'imdb_id', 'Title': 'title',
                'Genre': 'genre', 'Age Rating': 'age_rating', 'Release': 'release',
                'Runtime': 'runtime', 'IMDB Rating': 'imdb_rating', 'Metacritic Rating': 'meta_rating',
                'Director': 'director', 'Starring': 'starring', 'Cumulative Worldwide Gross': 'wwgross',
                'Budget': 'budget', 'Plot': 'plot'}

    def __init__(self, path_to_the_file='../datasets/links.csv'):
        try:
            if path_to_the_file != '../datasets/links.csv':
                raise Exception("Wrong file for this Class")
            else:
                self.links_file = path_to_the_file
                self.movies_file = '../datasets/movies.csv'
                self.imdb_file = '../datasets/imdb.csv'
                self.movies_data = {}
                with open(self.links_file, 'r', encoding='utf8') as links_f:
                    next(links_f)
                    # _ = links_f.readline()
                    self.links = {k: v for k, v, _ in [line.split(',') for line in links_f.readlines()]}
                with open(self.movies_file, 'r', encoding='utf8') as movies_f, open(self.imdb_file, 'r',
                                                                                    encoding='utf8') as imdb_f:
                    next(movies_f), next(imdb_f)
                    # _, _ = movies_f.readline(), imdb_f.readline()
                    for movie_line, imdb_line in zip(movies_f, imdb_f):
                        key_id, *_, genre = [i.strip() for i in movie_line.split(',')]
                        imdb_id, title, *other_data = [i.strip() for i in imdb_line.split(';')]
                        data_line = Links.FilmData(key_id, imdb_id, title, genre, *other_data)
                        self.movies_data.update({key_id: data_line})
        except Exception as e:
            print(e)
            sys.exit(1)

    @staticmethod
    def parse_imdb(movie_id, imdb_id):
        URL_SAMPLE = 'https://www.imdb.com/title/tt'
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
        url = f'{URL_SAMPLE}{imdb_id}/'
        responce = requests.get(url, headers=HEADERS)
        content = soup(responce.text, 'html.parser')
        json_text = content.find('script', id='__NEXT_DATA__', type='application/json').string.strip()
        json_data = json.loads(json_text)['props']['pageProps']
        parsed_data = Links.get_from_json(json_data, movie_id, imdb_id)
        return parsed_data

    @staticmethod
    def get_from_json(json_data, movie_id, imdb_id):
        info = json_data.get('aboveTheFoldData', {})
        money = json_data.get('mainColumnData', {})
        title = info.get('originalTitleText', {}).get('text', 'NO DATA')
        genre = info.get('genres', {}).get('genres', [{}])[0].get('text', 'NO DATA')
        age_rating = (info.get('certificate') or {}).get('rating', 'NO DATA')
        release_year = info.get('releaseYear', {}).get('year', 'NO DATA')
        runtime = str((info.get('runtime') or {}).get('seconds', 'NO DATA'))
        imdb_rating = info.get('ratingsSummary', {}).get('aggregateRating', 'NO DATA')
        meta_rating = (info.get('metacritic') or {}).get('metascore', {}).get('score', 'NO DATA')
        director = info.get('directorsPageTitle', [{}])[0].get('credits', [{}])[0].get('name', {}).get('nameText',
                                                                                                       {}).get('text',
                                                                                                               'NO DATA')
        star = info.get('castPageTitle', {}).get('edges', [{}])[0].get('node', {}).get('name', {}).get('nameText',
                                                                                                       {}).get('text',
                                                                                                               'NO DATA')
        wwgross = str((money.get('worldwideGross') or {}).get('total', {}).get('amount', 'NO DATA'))
        budget = str((money.get('productionBudget', {}) or {}).get('budget', {}).get('amount', 'NO DATA'))
        plot = ((info.get('plot') or {}).get('plotText', {}).get('plainText', 'NO DATA')).replace(';', '')
        return Links.FilmData(movie_id, imdb_id, title, genre, age_rating, release_year,
                              runtime, imdb_rating, meta_rating, director, star,
                              wwgross, budget, plot)

    def get_imdb(self, list_of_movies, list_of_fields):
        """
        The method returns a list of lists [movieId, field1, field2, field3, ...] for the list of movies given as the argument (movieId).
        For example, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
        The values should be parsed from the IMDB webpages of the movies.
        Sort it by movieId descendingly.
        """
        result = []
        list_of_fields = [field for field in list_of_fields if field in Links.data_map]
        for movie_id in list_of_movies:
            movie_id, temp = str(movie_id), []
            if movie_id not in self.movies_data:
                if movie_id in self.links:
                    imdb_id = self.links[movie_id]
                    try:
                        parsed = Links.parse_imdb(movie_id, imdb_id)
                        self.movies_data.update({movie_id: parsed})
                    except Exception as e:
                        print(f'An error occured while parsing this {imdb_id=}\n{e}')
                        continue
                else:
                    continue
            film = self.movies_data[movie_id]
            for field in list_of_fields:
                temp.append(getattr(film, Links.data_map[field]))
            result.append(temp)
        return sorted(result, key=lambda x: int(x[0]), reverse=True) if result else []

    def top_directors(self, n):
        """
        The method returns a dict with top-n directors where the keys are directors and
        the values are numbers of movies created by them. Sort it by numbers descendingly.
        """
        d = {}
        for line in self.movies_data.values():
            d[line.director] = d.get(line.director, 0) + 1
        directors = {k: v for k, v in sorted(d.items(), key=lambda x: x[1], reverse=True)[:n]}
        return directors

    def _get_unique_title(self, title, existing_titles):
        """
        Return unique title by adding (1), (2) if this title have another movie
        """
        base_title = title
        counter = 1
        while base_title in existing_titles:
            base_title = f"{title} ({counter})"
            counter += 1
        return base_title

    def most_expensive(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their budgets. Sort it by budgets descendingly.
        """
        budgets = {}
        sorted_by_budgets = sorted(self.movies_data.values(), key=lambda x: int(x.budget) if x.budget.isdigit() else -1,
                                   reverse=True)[:n]
        for film in sorted_by_budgets:
            if film.budget != 'NO DATA':
                unique_title = self._get_unique_title(film.title, budgets.keys())
                budgets.update({unique_title: int(film.budget)})
        return budgets

    def most_profitable(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the difference between cumulative worldwide gross and budget.
        Sort it by the difference descendingly.
        """
        profits = {}
        sorted_by_profits = sorted(self.movies_data.values(),
                                   key=lambda x: int(x.wwgross) - int(x.budget)
                                   if all([x.wwgross.isdigit(), x.budget.isdigit()])
                                   else -1, reverse=True)[:n]
        for film in sorted_by_profits:
            if all(i != 'NO DATA' for i in [film.wwgross, film.budget]):
                unique_title = self._get_unique_title(film.title, profits.keys())
                profits.update({unique_title: int(film.wwgross) - int(film.budget)})
        return profits

    def longest(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their runtime. If there are more than one version – choose any.
        Sort it by runtime descendingly.
        """
        runtimes = {}
        sorted_by_runtime = sorted([i for i in self.movies_data.values() if i.runtime.isdigit()],
                                   key=lambda x: int(x.runtime), reverse=True)[:n]
        for film in sorted_by_runtime:
            unique_title = self._get_unique_title(film.title, runtimes.keys())
            runtimes.update({unique_title: int(film.runtime) // 60})
        return runtimes

    def top_cost_per_minute(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the budgets divided by their runtime. The budgets can be in different currencies – do not pay attention to it.
        The values should be rounded to 2 decimals. Sort it by the division descendingly.
        """
        costs = {}
        srt_by_cost_per_minute = sorted(
            (i for i in self.movies_data.values() if i.budget.isdigit() and i.runtime.isdigit()),
            key=lambda x: int(x.budget) / int(x.runtime), reverse=True)[:n]
        for film in srt_by_cost_per_minute:
            unique_title = self._get_unique_title(film.title, costs.keys())
            costs.update({unique_title: round(int(film.budget) / int(film.runtime),2)})
        return costs

    def most_common_words(self, n):
        """
        The method returns a dictionary with the top most frequently occurring words in
        movie plot descriptions, where the keys are the original words and the values are
        their quantities, sorted in descending order.
        """
        top_words, except_words = {}, (
        'the', 'and', 'his', 'with', 'their', 'her', 'for', 'who', 'but', 'from', 'when', 'that', 'him', 'they', 'has',
        'are', 'she', 'into', 'while', 'after', 'out', 'them', 'will', 'have', 'about', 'can', 'where')
        for line in self.movies_data.values():
            plot_words = [i.strip('",:;().!?').lower() for i in line.plot.split()]
            for word in plot_words:
                if word not in except_words and len(word) > 2:
                    top_words[word] = top_words.get(word, 0) + 1
        return {k: v for k, v in sorted(top_words.items(), key=lambda x: x[1], reverse=True)[:n]}

    def most_controversial(self, n):
        """
        The method returns a dictionary with top movies, where the keys are the movie
        titles and the values are the difference between the IMDB and Metascore ratings,
        sorted in descending order.
        """
        result = {}
        for line in self.movies_data.values():
            if line.imdb_rating != 'NO DATA' and line.meta_rating != 'NO DATA':
                imdb, meta, title = float(line.imdb_rating) * 10, int(line.meta_rating), line.title
                result[title] = abs(imdb - meta)
        result = {k: v for k, v in sorted(result.items(), key=lambda x: x[1], reverse=True)[:n]}
        return result

    def top_stars(self, n):
        """
        The method returns a dictionary with the top most frequently occurring actors
        in leading roles, where the keys are names and the values are their quantities,
        sorted in descending order.
        """
        top_stars = {}
        for line in self.movies_data.values():
            if (star := line.starring) != 'NO DATA':
                top_stars[star] = top_stars.get(star, 0) + 1
        top_stars = {k: v for k, v in sorted(top_stars.items(), key=lambda x: x[1], reverse=True)[:n]}
        return top_stars



class Test:
    """
    Tests for Movies 
    """
    @pytest.fixture
    def class_movies(self):
        filepath = '../datasets/movies.csv'
        cls_movies = Movies(filepath)
        return cls_movies

    def test_dist_by_release_type_of_return(self, class_movies):
        obj = class_movies.dist_by_release()
        assert isinstance(obj, dict)

    def test_dist_by_release_type_of_elem(self,class_movies):
        obj = class_movies.dist_by_release()
        for key, value in obj.items():
            assert isinstance(key,int)
            assert isinstance(value,int)

    def test_dist_by_release_right_sort(self,class_movies):
        obj = class_movies.dist_by_release()
        lst = [item[1] for item in obj.items()]
        assert all(lst[i] >= lst[i + 1] for i in range(len(lst) - 1))

    def test_dist_by_release_calc(self,class_movies):
        obj = class_movies.dist_by_release()
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {1996: 62, 1995: 56, 2002: 54, 1998: 50, 1994: 45}



    def test_dist_by_genres_type_of_return(self, class_movies):
        obj = class_movies.dist_by_genres()
        assert isinstance(obj, dict)

    def test_dist_by_genres_type_of_elem(self,class_movies):
        obj = class_movies.dist_by_genres()
        for key, value in obj.items():
            assert isinstance(key,str)
            assert isinstance(value,int)

    def test_dist_by_genres_right_sort(self,class_movies):
        obj = class_movies.dist_by_genres()
        lst = [item[1] for item in obj.items()]
        assert all(lst[i] >= lst[i + 1] for i in range(len(lst) - 1))

    def test_dist_by_genres_calc(self,class_movies):
        obj = class_movies.dist_by_genres()
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'Drama': 563, 'Comedy': 343, 'Romance': 246, 'Thriller': 183, 'Adventure': 127}


    def test_most_genres_type_of_return(self, class_movies):
        obj = class_movies.most_genres(1000)
        assert isinstance(obj, dict)

    def test_most_genres_type_of_elem(self,class_movies):
        obj = class_movies.most_genres(1000)
        for key, value in obj.items():
            assert isinstance(key,str)
            assert isinstance(value,int)

    def test_most_genres_right_sort(self,class_movies):
        obj = class_movies.most_genres(1000)
        lst = [item[1] for item in obj.items()]
        assert all(lst[i] >= lst[i + 1] for i in range(len(lst) - 1))

    def test_most_genres_calc(self,class_movies):
        obj = class_movies.most_genres(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'Who Framed Roger Rabbit?': 7, 'Lion King, The': 6, 'Beauty and the Beast': 6, 'Space Jam': 6, 'Shrek': 6}

    """
    Tests for Tags
    """
    @pytest.fixture
    def class_tags(self):
        filepath = '../datasets/tags.csv'
        cls_tags = Tags(filepath)
        return cls_tags


    def test_most_words_type_of_return(self, class_tags):
        obj = class_tags.most_words(1000)
        assert isinstance(obj, dict)


    def test_most_words_type_of_elem(self, class_tags):
        obj = class_tags.most_words(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_most_words_right_sort(self, class_tags):
        obj = class_tags.most_words(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        lst_of_tag_names = [item[0] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))
        assert len(lst_of_tag_names) == len(set(lst_of_tag_names))

    def test_most_words_calc(self,class_tags):
        obj = class_tags.most_words(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'VILLAIN NONEXISTENT OR NOT NEEDED FOR GOOD STORY': 8, 'IT WAS MELODRAMATIC AND KIND OF DUMB': 7, 'OSCAR (BEST EFFECTS - VISUAL EFFECTS)': 6, 'OSCAR (BEST MUSIC - ORIGINAL SCORE)': 6, 'A DINGO ATE MY BABY': 5}


    def test_longest_type_of_return(self, class_tags):
        obj = class_tags.longest(1000)
        assert isinstance(obj, list)


    def test_longest_type_of_elem(self, class_tags):
        obj = class_tags.longest(1000)
        for item in obj:
            assert isinstance(item, str)


    def test_longest_right_sort(self, class_tags):
        obj = class_tags.longest(1000)
        assert all(len(obj[i]) >= len(obj[i + 1]) for i in range(len(obj) - 1))
        assert len(obj) == len(set(obj))

    def test_longest_calc(self,class_tags):
        obj = class_tags.longest(1000)
        test_obj = set(obj[:5])
        assert test_obj == {'VILLAIN NONEXISTENT OR NOT NEEDED FOR GOOD STORY', 'R:DISTURBING VIOLENT CONTENT INCLUDING RAPE', 'ACADEMY AWARD (BEST SUPPORTING ACTRESS)', 'OSCAR (BEST EFFECTS - VISUAL EFFECTS)', 'IT WAS MELODRAMATIC AND KIND OF DUMB'}


    def test_most_words_and_longest_type_of_return(self, class_tags):
        obj = class_tags.most_words_and_longest(1000)
        assert isinstance(obj, list)


    def test_most_words_and_longest_type_of_elem(self, class_tags):
        obj = class_tags.most_words_and_longest(1000)
        for item in obj:
            assert isinstance(item, str)


    def test_most_words_and_longest_right_sort(self, class_tags):
        print("По условию данная функция не требует сортировки, только поиск пересечения")

    def test_most_words_and_longest_calc(self,class_tags):
        obj = class_tags.most_words_and_longest(5)
        test_obj = set(obj)
        assert test_obj == {'IT WAS MELODRAMATIC AND KIND OF DUMB', 'OSCAR (BEST EFFECTS - VISUAL EFFECTS)', 'VILLAIN NONEXISTENT OR NOT NEEDED FOR GOOD STORY'}


    def test_most_popular_type_of_return(self, class_tags):
        obj = class_tags.most_popular(1000)
        assert isinstance(obj, dict)


    def test_most_popular_type_of_elem(self, class_tags):
        obj = class_tags.most_popular(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_most_popular_right_sort(self, class_tags):
        obj = class_tags.most_popular(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        lst_of_tag_names = [item[0] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))
        assert len(lst_of_tag_names) == len(set(lst_of_tag_names))

    def test_most_popular_calc(self,class_tags):
        obj = class_tags.most_popular(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'IN NETFLIX QUEUE': 65, 'ATMOSPHERIC': 23, 'DISNEY': 21, 'TWIST ENDING': 16, 'ALIENS': 15}

    def test_tags_with_type_of_return(self, class_tags):
        obj = class_tags.tags_with('war')
        assert isinstance(obj, list)


    def test_tags_with_type_of_elem(self, class_tags):
        obj = class_tags.tags_with('war')
        for item in obj:
            assert isinstance(item, str)


    def test_tags_with_right_sort(self, class_tags):
        obj = class_tags.tags_with('war')
        assert all(obj[i] <= obj[i + 1] for i in range(len(obj) - 1))
        assert len(obj) == len(set(obj))

    def test_tags_with_calc(self,class_tags):
        obj = class_tags.tags_with('war')
        test_obj = obj
        assert test_obj == ['ANTI-WAR', 'CIVIL WAR', 'COLD WAR', 'GULF WAR', 'NUCLEAR WAR', 'WAR', 'WORLD WAR I', 'WORLD WAR II']


    """
    Tests for Links
    """
    @pytest.fixture
    def class_links(self):
        filepath = '../datasets/links.csv'
        cls_links = Links(filepath)
        return cls_links

    def test_get_imdb_type_of_return(self, class_links):
        obj = class_links.get_imdb([1,2,10,15],['movieID', 'Title', 'Director', 'Cumulative Worldwide Gross', 'Runtime'])
        assert isinstance(obj, list)


    def test_get_imdb_type_of_elem(self, class_links):
        obj = class_links.get_imdb([1,2,10,15],['movieID', 'Title', 'Director', 'Cumulative Worldwide Gross', 'Runtime'])
        for item in obj:
            assert isinstance(item, list)


    def test_get_imdb_right_sort(self, class_links):
        obj = class_links.get_imdb([1,2,10,15],['movieID', 'Title', 'Director', 'Cumulative Worldwide Gross', 'Runtime'])
        lst = [int(item[0]) for item in obj]
        assert all(lst[i] >= lst[i + 1] for i in range(len(lst) - 1))

    def test_get_imdb_calc(self, class_links):
        obj = class_links.get_imdb([1,2,10,15],['movieID', 'Title', 'Director', 'Cumulative Worldwide Gross', 'Runtime'])
        test_obj = obj
        assert test_obj == [['15', 'Cutthroat Island', 'Renny Harlin', '10017322', '7440'], ['10', 'GoldenEye', 'Martin Campbell', '352194034', '7800'], ['2', 'Jumanji', 'Joe Johnston', '262821940', '6240'], ['1', 'Toy Story', 'John Lasseter', '394436586', '4860']]


    def test_top_directors_type_of_return(self, class_links):
        obj = class_links.top_directors(1000)
        assert isinstance(obj, dict)


    def test_top_directors_type_of_elem(self, class_links):
        obj = class_links.top_directors(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_top_directors_right_sort(self, class_links):
        obj = class_links.top_directors(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_top_directors_calc(self, class_links):
        obj = class_links.top_directors(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'Alfred Hitchcock': 16, 'Steven Spielberg': 13, 'Stanley Kubrick': 9, 'Ron Howard': 8, 'Ivan Reitman': 8}

    def test_most_expensive_type_of_return(self, class_links):
        obj = class_links.most_expensive(1000)
        assert isinstance(obj, dict)


    def test_most_expensive_type_of_elem(self, class_links):
        obj = class_links.most_expensive(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_most_expensive_right_sort(self, class_links):
        obj = class_links.most_expensive(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_most_expensive_calc(self, class_links):
        obj = class_links.most_expensive(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'The Name of the Rose': 30000000000, 'La vita è bella': 15000000000, 'Mononoke-hime': 2400000000, 'Akira': 1100000000, 'Titanic': 200000000}


    def test_most_profitable_type_of_return(self, class_links):
        obj = class_links.most_profitable(1000)
        assert isinstance(obj, dict)


    def test_most_profitable_type_of_elem(self, class_links):
        obj = class_links.most_profitable(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_most_profitable_right_sort(self, class_links):
        obj = class_links.most_profitable(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_most_profitable_calc(self, class_links):
        obj = class_links.most_profitable(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'Titanic': 2064812968, 'Jurassic Park': 1041379926, 'The Lion King': 934161373, 'Star Wars: Episode I - The Phantom Menace': 931515409, "Harry Potter and the Sorcerer's Stone": 901414475}

    def test_longest_link_type_of_return(self, class_links):
        obj = class_links.longest(1000)
        assert isinstance(obj, dict)


    def test_longest_link_type_of_elem(self, class_links):
        obj = class_links.longest(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_longest_link_right_sort(self, class_links):
        obj = class_links.longest(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_longest_link_calc(self, class_links):
        obj = class_links.longest(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'The Greatest Story Ever Told': 260, 'Hamlet': 242, 'Gone with the Wind': 238, 'Lawrence of Arabia': 227, 'Shichinin no samurai': 207}


    def test_top_cost_per_minute_type_of_return(self, class_links):
        obj = class_links.top_cost_per_minute(1000)
        assert isinstance(obj, dict)


    def test_top_cost_per_minute_type_of_elem(self, class_links):
        obj = class_links.top_cost_per_minute(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, float)


    def test_top_cost_per_minute_right_sort(self, class_links):
        obj = class_links.top_cost_per_minute(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_top_cost_per_minute_calc(self, class_links):
        obj = class_links.top_cost_per_minute(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'The Name of the Rose': 3846153.85, 'La vita è bella': 2155172.41, 'Mononoke-hime': 300751.88, 'Akira': 147849.46, 'Le peuple migrateur': 27210.88}


    """
    Tests for bonus methods
    """
    def test_most_common_words_type_of_return(self, class_links):
        obj = class_links.most_common_words(1000)
        assert isinstance(obj, dict)


    def test_most_common_words_type_of_elem(self, class_links):
        obj = class_links.most_common_words(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_most_common_words_right_sort(self, class_links):
        obj = class_links.most_common_words(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_most_common_words_calc(self, class_links):
        obj = class_links.most_common_words(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'young': 115, 'new': 98, 'two': 92, 'man': 88, 'life': 82}

    def test_most_controversial_type_of_return(self, class_links):
        obj = class_links.most_controversial(1000)
        assert isinstance(obj, dict)


    def test_most_controversial_type_of_elem(self, class_links):
        obj = class_links.most_controversial(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, float)


    def test_most_controversial_right_sort(self, class_links):
        obj = class_links.most_controversial(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_most_controversial_calc(self, class_links):
        obj = class_links.most_controversial(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'Billy Madison': 48.0, '8MM': 45.0, 'Patch Adams': 42.0, 'Happy Gilmore': 39.0, 'UHF': 37.0}

    def test_top_stars_type_of_return(self, class_links):
        obj = class_links.top_stars(1000)
        assert isinstance(obj, dict)


    def test_top_stars_type_of_elem(self, class_links):
        obj = class_links.top_stars(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_top_stars_right_sort(self, class_links):
        obj = class_links.top_stars(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_top_stars_calc(self, class_links):
        obj = class_links.top_stars(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj =={'Tom Hanks': 13, 'Robert De Niro': 10, 'Tom Cruise': 10, 'Harrison Ford': 9, 'Al Pacino': 9}

    """
    Tests for Ratings
    """
    @pytest.fixture
    def class_ratings_movies(self):
        filepath = '../datasets/ratings.csv'
        cls_ratings = Ratings.Movies(filepath)
        return cls_ratings


    def test_dist_by_year_type_of_return(self, class_ratings_movies):
        obj = class_ratings_movies.dist_by_year()
        assert isinstance(obj, dict)


    def test_dist_by_year_type_of_elem(self, class_ratings_movies):
        obj = class_ratings_movies.dist_by_year()
        for key, value in obj.items():
            assert isinstance(key, int)
            assert isinstance(value, int)


    def test_dist_by_year_right_sort(self, class_ratings_movies):
        obj = class_ratings_movies.dist_by_year()
        lst_of_counts = [item[0] for item in obj.items()]
        assert all(lst_of_counts[i] <= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_dist_by_year_calc(self, class_ratings_movies):
        obj = class_ratings_movies.dist_by_year()
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {1996: 3564, 1997: 1059, 1998: 275, 1999: 1388, 2000: 4306}

    def test_dist_by_rating_type_of_return(self, class_ratings_movies):
        obj = class_ratings_movies.dist_by_rating()
        assert isinstance(obj, dict)


    def test_dist_by_rating_type_of_elem(self, class_ratings_movies):
        obj = class_ratings_movies.dist_by_rating()
        for key, value in obj.items():
            assert isinstance(key, float)
            assert isinstance(value, int)


    def test_dist_by_rating_right_sort(self, class_ratings_movies):
        obj = class_ratings_movies.dist_by_rating()
        lst_of_counts = [item[0] for item in obj.items()]
        assert all(lst_of_counts[i] <= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_dist_by_rating_calc(self, class_ratings_movies):
        obj = class_ratings_movies.dist_by_rating()
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {0.5: 256, 1.0: 708, 1.5: 338, 2.0: 1901, 2.5: 1370}

    def test_top_by_num_of_ratings_type_of_return(self, class_ratings_movies):
        obj = class_ratings_movies.top_by_num_of_ratings(1000)
        assert isinstance(obj, dict)


    def test_top_by_num_of_ratings_type_of_elem(self, class_ratings_movies):
        obj = class_ratings_movies.top_by_num_of_ratings(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_top_by_num_of_ratings_right_sort(self, class_ratings_movies):
        obj = class_ratings_movies.top_by_num_of_ratings(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_top_by_num_of_ratings_calc(self, class_ratings_movies):
        obj = class_ratings_movies.top_by_num_of_ratings(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'Forrest Gump': 328, 'Shawshank Redemption, The': 316, 'Pulp Fiction': 306, 'Silence of the Lambs, The': 278, 'Matrix, The': 277}

    def test_top_ratings_type_of_return(self, class_ratings_movies):
        obj = class_ratings_movies.top_by_ratings(1000)
        obj2 = class_ratings_movies.top_by_ratings(1000,'median')
        assert isinstance(obj, dict)
        assert isinstance(obj2, dict)


    def test_top_by_ratings_type_of_elem(self, class_ratings_movies):
        obj = class_ratings_movies.top_by_ratings(1000)
        obj2 = class_ratings_movies.top_by_ratings(1000, 'median')
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, float)

        for key, value in obj2.items():
            assert isinstance(key, str)
            assert isinstance(value, float)



    def test_top_by_ratings_right_sort(self, class_ratings_movies):
        obj = class_ratings_movies.top_by_ratings(1000)
        obj2 = class_ratings_movies.top_by_ratings(1000,'median')
        lst_of_counts = [item[1] for item in obj.items()]
        lst_of_counts2 = [item[1] for item in obj2.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))
        assert all(lst_of_counts2[i] >= lst_of_counts2[i + 1] for i in range(len(lst_of_counts2) - 1))

    def test_top_by_ratings_calc(self, class_ratings_movies):
        obj = class_ratings_movies.top_by_ratings(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'Wings of the Dove, The': 4.7, 'Paths of Glory': 4.59, 'Last Picture Show, The': 4.57, 'Secrets & Lies': 4.55, 'Ran': 4.5}

    def test_top_controversial_type_of_return(self, class_ratings_movies):
        obj = class_ratings_movies.top_controversial(1000)
        assert isinstance(obj, dict)


    def test_top_controversial_type_of_elem(self, class_ratings_movies):
        obj = class_ratings_movies.top_controversial(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, float)


    def test_top_controversial_right_sort(self, class_ratings_movies):
        obj = class_ratings_movies.top_controversial(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_top_controversial_calc(self, class_ratings_movies):
        obj = class_ratings_movies.top_controversial(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'Meatballs': 1.94, 'Blair Witch Project, The': 1.88, 'Home Alone 2: Lost in New York': 1.85, 'Romper Stomper': 1.73, 'Short Cuts': 1.73}


    @pytest.fixture
    def class_ratings_users(self):
        filepath = '../datasets/ratings.csv'
        cls_ratings = Ratings.Users(filepath)
        return cls_ratings

    def test_user_activity_type_of_return(self, class_ratings_users):
        obj = class_ratings_users.user_activity()
        assert isinstance(obj, dict)


    def test_user_activity_type_of_elem(self, class_ratings_users):
        obj = class_ratings_users.user_activity()
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_user_activity_right_sort(self, class_ratings_users):
        obj = class_ratings_users.user_activity()
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_user_activity_calc(self, class_ratings_users):
        obj = class_ratings_users.user_activity()
        test_obj = obj

        assert test_obj['1 mark'] == 5
        assert test_obj['2-5 marks'] == 13
        assert test_obj['6-9 marks'] == 35
        assert test_obj['10-19 marks'] == 125
        assert test_obj['20-49 marks'] == 205
        assert test_obj['50-99 marks'] == 124
        assert test_obj['100-249 marks'] == 84
        assert test_obj['250-499 marks'] == 16
        assert test_obj['500+ marks'] == 3


    def test_user_tendency_type_of_return(self, class_ratings_users):
        obj = class_ratings_users.user_tendency()
        obj2 = class_ratings_users.user_tendency('median')
        assert isinstance(obj, dict)
        assert isinstance(obj2, dict)


    def test_user_tendency_type_of_elem(self, class_ratings_users):
        obj = class_ratings_users.user_tendency()
        obj2 = class_ratings_users.user_tendency('median')
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, int)

        for key, value in obj2.items():
            assert isinstance(key, str)
            assert isinstance(value, int)


    def test_user_tendency_right_sort(self, class_ratings_users):
        obj = class_ratings_users.user_tendency()
        obj2 = class_ratings_users.user_tendency('median')
        lst_of_counts = [item[1] for item in obj.items()]
        lst_of_counts2 = [item[1] for item in obj2.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))
        assert all(lst_of_counts2[i] >= lst_of_counts2[i + 1] for i in range(len(lst_of_counts2) - 1))

    def test_user_tendency_calc(self, class_ratings_users):
        obj = class_ratings_users.user_tendency()
        test_obj = obj

        assert test_obj['0.5-1.0 marks'] == 1
        assert test_obj['1.0-1.99 marks'] == 2
        assert test_obj['2.0-2.99 marks'] == 29
        assert test_obj['3.0-3.99 marks'] == 336
        assert test_obj['4.0-4.49 marks'] == 197
        assert test_obj['4.5-5.0 marks'] == 34

    def test_user_controversial_type_of_return(self, class_ratings_users):
        obj = class_ratings_users.user_controversial(1000)
        assert isinstance(obj, dict)


    def test_user_controversial_type_of_elem(self, class_ratings_users):
        obj = class_ratings_users.user_controversial(1000)
        for key, value in obj.items():
            assert isinstance(key, str)
            assert isinstance(value, float)


    def test_user_controversial_right_sort(self, class_ratings_users):
        obj = class_ratings_users.user_controversial(1000)
        lst_of_counts = [item[1] for item in obj.items()]
        assert all(lst_of_counts[i] >= lst_of_counts[i + 1] for i in range(len(lst_of_counts) - 1))

    def test_user_controversial_calc(self, class_ratings_users):
        obj = class_ratings_users.user_controversial(1000)
        test_obj = dict(list(obj.items())[:5])
        assert test_obj == {'259': 2.9, '598': 2.81, '461': 2.67, '329': 2.6, '393': 2.6}
