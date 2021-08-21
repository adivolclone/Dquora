from django import forms

from markdownx.fields import MarkdownxFormField

from dquora.qa.models import Question


class QuestionForm(forms.ModelForm):
    status = forms.CharField(widget=forms.HiddenInput)  # 隐藏显示
    content = MarkdownxFormField()

    class Meta:
        model = Question
        fields = ['title', 'status', 'content', 'tags']
