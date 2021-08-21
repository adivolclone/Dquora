from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from dquora.qa.models import Question, Answer
from dquora.helpers import ajax_required
from dquora.qa.forms import QuestionForm
from dquora.notifications.views import notification_handler


# Create your views here.

class QuestionListView(ListView):
    """所有问题页"""
    model = Question
    paginate_by = 10
    context_object_name = 'questions'
    template_name = 'qa/question_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(QuestionListView, self).get_context_data()
        context['popular_tags'] = Question.objects.get_counted_tags()  # 标签字典
        context['active'] = 'all'  # 有三个导航栏
        return context


class UnansweredQuestionListView(QuestionListView):
    """未接受回答的问题"""

    def get_queryset(self):
        return Question.objects.get_unanswered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(UnansweredQuestionListView, self).get_context_data()
        context['active'] = 'unanswered'  # 有三个导航栏
        return context


class AnsweredQuestionListView(QuestionListView):
    """已接受回答的问题"""

    def get_queryset(self):
        return Question.objects.get_answered()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(AnsweredQuestionListView, self).get_context_data()
        context['active'] = 'answered'  # 有三个导航栏
        return context


class QuestionCreateView(LoginRequiredMixin, CreateView):
    form_class = QuestionForm
    template_name = 'qa/question_form.html'
    message = "问题已提交！"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(QuestionCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy("qa:unanswered_q")


class QuestionDetailView(LoginRequiredMixin, DetailView):
    model = Question
    context_object_name = 'question'
    template_name = 'qa/question_detail.html'


class AnswerCreateView(LoginRequiredMixin, CreateView):
    """回答问题"""
    model = Answer
    # 单个字段时，就不用建立ModelForm了，直接在view里用fields属性指定。
    fields = ['content']
    template_name = 'qa/answer_form.html'
    message = '您的问题已提交'

    def form_valid(self, form):
        form.instance.user = self.request.user
        # question_id，通过url路由设置的URL参数传递过来
        form.instance.question_id = self.kwargs['question_id']
        return super(AnswerCreateView, self).form_valid(form)

    def get_success_url(self):
        messages.success(self.request, self.message)
        return reverse_lazy('qa:question_detail', kwargs={'pk': self.kwargs['question_id']})


@login_required
@ajax_required
@require_http_methods(["POST"])
def question_vote(request):
    """给问题投票，AJAX POST请求"""
    question_id = request.POST["question"]
    value = True if request.POST["value"] == 'U' else False  # 'U'表示赞，'D'表示踩
    question = Question.objects.get(pk=question_id)
    users = question.votes.values_list('user', flat=True)  # 当前问题的所有投票用户
    # 点赞或踩一共五种情况，利用update_or_create（）简化为两种情况。
    if request.user.pk in users and (question.votes.get(user=request.user).value == value):
        question.votes.get(user=request.user).delete()
    else:
        question.votes.update_or_create(user=request.user, defaults={"value": value})

    """
    # 1.用户首次操作，点赞/踩
    if request.user.pk not in users:
        question.votes.update_or_create(user=request.user, defaults={"value": value})

    # 2.用户已近赞过，要取消赞/踩一下
    elif question.votes.get(user=request.user).value:
        if value:
            question.votes.get(user=request.user).delete()
        else:
            question.votes.update_or_create(user=request.user, defaults={"value": value})

    # 3.用户已踩过，取消踩/赞一下
    else:
        if not value:
            question.votes.get(user=request.user).delete()
        else:
            question.votes.update_or_create(user=request.user, defaults={"value": value})
    """

    return JsonResponse({"votes": question.total_votes()})


@login_required
@ajax_required
@require_http_methods(["POST"])
def answer_vote(request):
    """给回答投票，AJAX POST请求"""
    answer_id = request.POST["answer"]
    value = True if request.POST["value"] == 'U' else False  # 'U'表示赞，'D'表示踩
    answer = Answer.objects.get(uuid_id=answer_id)
    users = answer.votes.values_list('user', flat=True)  # 当前回答的所有投票用户

    if request.user.pk in users and (answer.votes.get(user=request.user).value == value):
        answer.votes.get(user=request.user).delete()
    else:
        answer.votes.update_or_create(user=request.user, defaults={"value": value})

    return JsonResponse({"votes": answer.total_votes()})


@login_required
@ajax_required
@require_http_methods(["POST"])
def accept_answer(request):
    """接受回答，AJAX POST请求
    已经被接受的回答用户不能取消"""
    answer_id = request.POST['answer']
    answer = Answer.objects.get(pk=answer_id)
    # 如果当前登录用户不是提问者，抛出权限拒绝错误
    if answer.question.user.username != request.user.username:
        raise PermissionDenied
    answer.accept_answer()
    # 接受回答后，通知文章作者
    notification_handler(request.user, answer.user, 'W', answer)
    return JsonResponse({'status': 'true'})
