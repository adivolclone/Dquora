from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DeleteView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy

from dquora.news.models import News
from dquora.helpers import ajax_required, AuthorRequiredMixin


# Create your views here.


class NewsListView(LoginRequiredMixin, ListView):
    """首页动态"""
    model = News
    paginate_by = 20
    template_name = 'news/news_list.html'

    def get_queryset(self):
        return News.objects.filter(reply=False)


class NewsDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = News
    template_name = 'news/news_confirm_delete.html'
    success_url = reverse_lazy('news:list')


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_new(request):
    """发送动态， AJAX POST 请求"""
    post = request.POST['post'].strip()
    if post:
        posted = News.objects.create(user=request.user, content=post)
        # 先渲染为html模板，然后返回给前端
        html = render_to_string('news/news_single.html', {'news': posted, 'request': request})
        return HttpResponse(html)
    else:
        return HttpResponseBadRequest("内容不能为空！")


@login_required
@ajax_required
@require_http_methods(['POST'])
def like(request):
    """点赞， AJAX POST 提交"""
    news_id = request.POST['news']
    news = News.objects.get(pk=news_id)
    user = request.user
    news.switch_like(user)
    return JsonResponse({'likes': news.count_likers()})


@login_required
@ajax_required
@require_http_methods(['GET'])
def get_thread(request):
    """返回动态的评论， AJAX GET 请求"""
    news_id = request.GET['news']
    news = News.objects.get(pk=news_id)
    # 没有评论时显示该动态
    news_html = render_to_string('news/news_single.html', {'news': news})
    # 有评论时，返回该动态下所有评论
    thread_html = render_to_string('news/news_thread.html', {'thread': news.get_thread()})
    return JsonResponse({
        'uuid': news_id,
        'news': news_html,
        'thread': thread_html
    })


@login_required
@ajax_required
@require_http_methods(['POST'])
def post_comment(request):
    """提交评论， AJAX POST 请求"""
    text = request.POST['reply'].strip()
    parent_id = request.POST['parent']
    # 获取该条动态
    parent = News.objects.get(pk=parent_id)
    if text:
        parent.reply_this(request.user, text)
        return JsonResponse({'comments': parent.comment_count()})
    else:
        return HttpResponseBadRequest('内容不能为空！')


@login_required
@ajax_required
@require_http_methods(['POST'])
def update_interactions(request):
    """点赞或评论的动作交互 引起的"""
    news_id = request.POST['id_value']
    news = News.objects.get(pk=news_id)
    return JsonResponse({'likes': news.count_likers(), 'comments': news.comment_count()})
