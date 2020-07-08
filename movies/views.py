from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Comment, Qna, Qnacomment
from .forms import MovieForm, ReviewForm, CommentForm, QnaForm, QnacommentForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from collections import Counter

# Create your views here.

def index(request):       
    movie_li = Movie.objects.order_by('-id')
    reviews = Review.objects.all()

    review_form = ReviewForm()

    paginator = Paginator(movie_li, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context={
        'movie_li':movie_li,
        'reviews':reviews,
        'page_obj':page_obj,
        'review_form': review_form,
    }

    return render(request, 'movies/index.html', context)

def review_board(request):
    reviews=Review.objects.all()
    review_form = ReviewForm()
    context={
        'reviews':reviews,
        'review_form': review_form,
    }
    return render(request, 'movies/review_board.html', context)

def review_create(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('movies:review_detail', review.movie.id, review.id)
    else:
        form = ReviewForm()
    context = {
        'form': form
    }
    return render(request, 'movies/review_form.html', context)

def review_detail(request, movie_id, review_id):
    movie = get_object_or_404(Movie, id=movie_id)
    review = get_object_or_404(Review, id=review_id)
    
    review_form = ReviewForm(instance=review)
    comment_form = CommentForm()
    context = {
        'movie':movie,
        'review': review,
        'review_form': review_form,
        'comment_form': comment_form,
    }
    return render(request, 'movies/review_detail.html', context)

def review_update(request, movie_id, review_id):
    movie = get_object_or_404(Movie, id=movie_id)
    review = get_object_or_404(Review, id=review_id)

    if request.user == review.user:
        if request.method == 'POST':
            review_form = ReviewForm(request.POST, instance=review)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user
                review.save()
                return redirect('movies:review_detail', movie.id, review.id)
        else:
            review_form = ReviewForm(instance=review)
        context = {
            'reivew_form': review_form,
        }
        return render(request, 'movies/review_form.html', context)
    else:
        return redirect('movies:index')

def review_delete(request, movie_id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user == review.user:
        review.delete()
    return redirect('movies:review_board')

def comment_create(request, movie_id, review_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    movie = get_object_or_404(Movie, id=movie_id)
    review = get_object_or_404(Review, id=review_id)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.user = request.user
        comment.review = review
        comment.save()
    return redirect('movies:review_detail', movie.id, review.id)

def comment_update(request, movie_id, review_id, comment_id):
    movie = get_object_or_404(Movie, id=movie_id)
    review = get_object_or_404(Review, id=review_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user:
        if request.method == 'POST':
            comment_form = CommentForm(request.POST, instance=comment)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.user = comment.user
                comment.save()
                return redirect('movies:review_detail', movie.id, review.id)
        else:
            comment_form = CommentForm(instance=comment)
        context = {
            'comment_form': comment_form,
        }

        return render(request, 'movies/comment_form.html', context)
    else:
        return redirect('movies:index')

def comment_delete(request, movie_id, review_id, comment_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
    return redirect('movies:review_detail', movie_id, review_id)


def movies_like(request, movie_id):
    user = request.user
    movie = get_object_or_404(Movie, id=movie_id)

    if movie.like_users.filter(id=user.id).exists():
        movie.like_users.remove(user)
        liked = False
    else:
        movie.like_users.add(user)
        liked = True

    context = {
        "liked" : liked,
        "count" : movie.like_users.count(),
    }

    return JsonResponse(context)

@login_required
def recommend(request, name):

    current_user = get_object_or_404(get_user_model(), username=name)

    directors = current_user.like_movies.exclude(Q(director__isnull=True) | Q(director=''))

    director_list = []

    like_movie_list = []

    director_names = []
    
    directors_movies = []

    for d in directors:
        director_list.append(d.director)
        like_movie_list.append(d.movie_title)

    director_most = Counter(director_list).most_common()

    for d in director_most:
        director_names.append(d[0])

    for d in director_names:
        movie_li = Movie.objects.filter(director=d).order_by('-rate')
        if len(movie_li) > 1:
            directors_movies.append(movie_li)

    context={
        'directors_movies' : directors_movies,
        'like_movie_list' : like_movie_list,
    }

    return render(request, 'movies/recommend.html', context)


#내가 좋아요한 영화 장르의 평점 순으로 30개 영화 추천하기
@login_required
def recommend2(request, name):
    person = get_object_or_404(get_user_model(), username=name) #유저
    like_movies=person.like_movies.all() # 내가 좋아요 누른 영화들
    movie_all = Movie.objects.all() # 평점으로 영화 줄세우기 
    reviews=Review.objects.all()
    
    genres={} #모든 장르
    

    if len(like_movies)>0: #좋아요 누른 영화가 1개 이상일 때
        
        for g in movie_all: #장르 개수를 세기위한 dictionary 만들기
            genres[g.genre]=0

        for movie in like_movies: #좋아요 누른 영화를 하나씩 뽑아서 뽑은 영화의 장르들을 dictionary에 넣기
            genres[movie.genre] += 1
        
        def f(x):
            return x[1]

        result=genres.items()

        genre=[] 
        
        for key, value in result:
            if value!=0:
                genre.append(key) #내가 좋아하는 장르만

        rates={}

        for movie in movie_all: # 모든 영화에서
            if movie.genre in genre:
                #좋아하는 장르가 있는 영화 제목과 평점을 불러오기
                rates[movie.movie_title]=float(movie.rate)
        
        res = sorted(rates.items(), key=f, reverse=True)  # 평점 내리차순으로 정렬

        recommend = []

        for movie in movie_all:
            for i in range(30):
                if movie.movie_title==res[i][0]:
                    recommend.append(movie)


    else:
        recommend=[]

    paginator = Paginator(recommend,6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        

    context={
        'recommend':recommend,
        'reviews':reviews,
        'page_obj':page_obj,
    }

    return render(request, 'movies/recommend2.html', context)

@login_required
def qna_board(request):
    qnas=Qna.objects.all()
    qna_form = QnaForm()
    context={
        'qnas':qnas,
        'qna_form': qna_form,
    }
    return render(request, 'movies/qna_board.html', context)


@login_required
def qna_create(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.method == 'POST':
        form = QnaForm(request.POST)
        if form.is_valid():
            qna = form.save(commit=False)
            qna.user = request.user
            qna.save()
            return redirect('movies:qna_detail', qna.id)
    else:
        form = QnaForm()
    context = {
        'form': form
    }
    return render(request, 'movies/qna_form.html', context)

def qna_detail(request, qna_id):
    qna = get_object_or_404(Qna, id=qna_id)
    qna_form = QnaForm(instance=qna)
    qnacomment_form = QnacommentForm()
    context = {
        'qna':qna,
        'qna_form': qna_form,
        'qnacomment_form':qnacomment_form,
    }
    return render(request, 'movies/qna_detail.html', context)

def qna_update(request,qna_id):
    qna = get_object_or_404(Qna, id=qna_id)

    if request.user == qna.user:
        if request.method == 'POST':
            qna_form = QnaForm(request.POST, instance=qna)
            if qna_form.is_valid():
                qna = qna_form.save(commit=False)
                qna.user = request.user
                qna.save()
                return redirect('movies:qna_detail', qna.id)
        else:
            qna_form = QnaForm(instance=qna)
        context = {
            'qna_form': qna_form,
        }
        return render(request, 'movies/qna_form.html', context)
    else:
        return redirect('movies:index')

def qna_delete(request, qna_id):
    qna = get_object_or_404(Qna, id=qna_id)
    if request.user == qna.user:
        qna.delete()
    return redirect('movies:qna_board')

def qnacomment_create(request, qna_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    qna = get_object_or_404(Qna, id=qna_id)
    qnacomment_form = QnacommentForm(request.POST)
    if qnacomment_form.is_valid():
        qnacomment = qnacomment_form.save(commit=False)
        qnacomment.user = request.user
        qnacomment.qna = qna
        qnacomment.save()
    return redirect('movies:qna_detail', qna.id)

def qnacomment_update(request, qna_id, qnacomment_id):
    qna = get_object_or_404(Qna, id=qna_id)
    qnacomment = get_object_or_404(Qnacomment, id=qnacomment_id)

    if request.user == qnacomment.user:
        if request.method == 'POST':
            qnacomment_form = QnacommentForm(request.POST, instance=qnacomment)
            if qnacomment_form.is_valid():
                qnacomment = qnacomment_form.save(commit=False)
                qnacomment.user = qnacomment.user
                qnacomment.save()
                return redirect('movies:qna_detail', qna.id)
        else:
            qnacomment_form = QnacommentForm(instance=qnacomment)
        context = {
            'qnacomment_form': qnacomment_form,
        }

        return render(request, 'movies/qnacomment_form.html', context)
    else:
        return redirect('movies:index')

def qnacomment_delete(request, qna_id, qnacomment_id):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.method == 'POST':
        qnacomment = get_object_or_404(Qnacomment, id=qnacomment_id)
        if request.user == qnacomment.user:
            qnacomment.delete()
    return redirect('movies:qna_detail', qna_id)