from django.contrib import admin
from .models import Movie, Review, Comment, Qna, Qnacomment

admin.site.register(Movie)
admin.site.register(Review)
admin.site.register(Comment)
admin.site.register(Qna)
admin.site.register(Qnacomment)

