from django.urls import path
from . import views

app_name = 'movies'

urlpatterns=[
    path('', views.index, name='index'),
    path('<int:movie_id>/like/', views.movies_like, name='movies_like'),

    path('review_board/', views.review_board, name='review_board'), #리뷰게시판
    path('review_board/create/', views.review_create, name='review_create'),
    path('review_board/<int:movie_id>/<int:review_id>/', views.review_detail, name='review_detail'),
    path('review_board/<int:movie_id>/<int:review_id>/update/', views.review_update, name='review_update'),
    path('review_board/<int:movie_id>/<int:review_id>/delete/', views.review_delete, name='review_delete'),

    path('comment/<int:movie_id>/<int:review_id>/create/', views.comment_create, name='comment_create'),
    path('comment/<int:movie_id>/<int:review_id>/<int:comment_id>/update/', views.comment_update, name='comment_update'),
    path('comment/<int:movie_id>/<int:review_id>/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),

    path('recommend/<str:name>', views.recommend, name='recommend'),
    path('recommend2/<str:name>', views.recommend2, name='recommend2'),

    path('qna_board/', views.qna_board, name='qna_board'),
    path('qna_board/create/', views.qna_create, name='qna_create'),
    path('qna_board/<int:qna_id>', views.qna_detail, name='qna_detail'),
    path('qna_board/<int:qna_id>/update', views.qna_update, name='qna_update'),
    path('qna_board/<int:qna_id>/delete', views.qna_delete, name='qna_delete'),

    path('qnacomment/<int:qna_id>/create/', views.qnacomment_create, name='qnacomment_create'),
    path('qnacomment/<int:qna_id>/<int:qnacomment_id>/update/', views.qnacomment_update, name='qnacomment_update'),
    path('qnacomment/<int:qna_id>/<int:qnacomment_id>/delete/', views.qnacomment_delete, name='qnacomment_delete'),

]