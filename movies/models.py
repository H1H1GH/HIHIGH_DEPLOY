from django.db import models
from django.conf import settings
import json
import requests
from decouple import config

class Movie(models.Model):
    movie_title = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    director = models.CharField(max_length=100)
    overview = models.TextField()
    release_date = models.CharField(max_length=50)
    poster_path = models.CharField(max_length=150)
    backdrop_path = models.CharField(max_length=150)
    movie_num = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=3, decimal_places=2)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_movies', blank=True)
    

    def __str__(self):
        return self.movie_title

    @classmethod
    def get_movie_data(mov, first_page, last_page):
        API_TMD_KEY = config('API_TMD_KEY')
        for num in range(first_page, last_page):

            page_num = str(num)
            MOVIE_LIST_URL = f"https://api.themoviedb.org/3/discover/movie?api_key={API_TMD_KEY}&language=ko-KR&page={page_num}"
            movie_list_data = requests.get(MOVIE_LIST_URL)
            result_data = movie_list_data.json().get('results')

            for res in result_data:
                movie_num = res.get('id')
                movie_title = res.get('title')
                if res.get('poster_path'):
                    poster_path = "https://image.tmdb.org/t/p/original"+ res.get('poster_path')
                else:
                    poster_path = ""
                if res.get('backdrop_path'):
                    backdrop_path = "https://image.tmdb.org/t/p/original"+ res.get('backdrop_path')
                else:
                    backdrop_path = ""
                rate = res.get('vote_average')
                
                MOVIE_DETAIL_URL = f"https://api.themoviedb.org/3/movie/{movie_num}?api_key={API_TMD_KEY}&language=ko-KR"
                movie_detail_data = requests.get(MOVIE_DETAIL_URL)

                if movie_detail_data.json().get('genres'):
                    genre = movie_detail_data.json().get('genres')[0].get('name')
                else:
                    genre = ""

                overview = str(movie_detail_data.json().get('overview'))
                release_date = str(movie_detail_data.json().get('release_date'))

                MOVIE_CREDITS_URL = f"https://api.themoviedb.org/3/movie/{movie_num}/credits?api_key={API_TMD_KEY}"
                credits_data = requests.get(MOVIE_CREDITS_URL)
                directors_data = credits_data.json().get('crew')
                
                for i in range(len(directors_data)):
                    if directors_data[i].get('job') =='Director':
                        director = directors_data[i].get('name')
                        break
                    else:
                        director = ""

                mov.objects.get_or_create(
                    movie_title=movie_title,
                    genre=genre,
                    director=director,
                    overview=overview,
                    release_date=release_date,
                    poster_path= poster_path,
                    backdrop_path=backdrop_path,
                    movie_num=movie_num,
                    rate = rate,
                )



class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    rank = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Qna(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Qnacomment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qna = models.ForeignKey(Qna, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)