from django import forms
from .models import Movie, Review, Comment, Qna, Qnacomment

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = '__all__'

class ReviewForm(forms.ModelForm):
    PICKS = [
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
    ]

    rank = forms.ChoiceField(choices=PICKS, widget=forms.Select())

    class Meta:
        model = Review
        fields = ['movie', 'title', 'rank', 'content']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class QnaForm(forms.ModelForm):
    class Meta:
        model = Qna
        fields = ['title','content']

class QnacommentForm(forms.ModelForm):
    class Meta:
        model = Qnacomment
        fields = ['content']