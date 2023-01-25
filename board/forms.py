from django import forms
from board.models import Question, Answer


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question  # 사용할 모델
        fields = ['subject', 'content', 'route', 'time']  # QuestionForm에서 사용할 Question 모델의 속성
        labels = {
            'subject': '제목',
            'route' : '경로',
            'time' : '경매 마감',
            'content': '경매 시작가',
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content': '입찰금액',
        }
