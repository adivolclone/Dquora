from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from django_comments.signals import comment_was_posted

from dquora.articles.models import Article
from dquora.articles.forms import ArticleForm
from dquora.helpers import AuthorRequiredMixin
from dquora.notifications.views import notification_handler


# Create your views here.


class ArticleListView(ListView):
    """已发布的文章列表"""
    model = Article
    paginate_by = 10
    context_object_name = 'articles'
    template_name = 'articles/article_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ArticleListView, self).get_context_data()
        context['popular_tags'] = Article.objects.get_counted_tags()
        return context

    def get_queryset(self):
        return Article.objects.get_published()


class DraftListView(ArticleListView):
    """草稿箱文章列表"""

    def get_queryset(self):
        """当前用户的草稿"""
        return Article.objects.filter(user=self.request.user).get_drafts()


class ArticleCreateView(LoginRequiredMixin, CreateView):
    """发表文章"""
    model = Article
    form_class = ArticleForm
    template_name = 'articles/article_create.html'
    message = '您的文章已创建成功！'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ArticleCreateView, self).form_valid(form)

    # 创建成功后跳转
    def get_success_url(self):
        # 将消息传递给下一次请求
        messages.success(self.request, self.message)
        return reverse_lazy('articles:list')


class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'articles/article_detail.html'


class ArticleEditView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    """编辑文章"""
    model = Article
    form_class = ArticleForm
    message = '您的文章编辑成功！'
    template_name = 'articles/article_update.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ArticleEditView, self).form_valid(form)

    # 创建成功后跳转
    def get_success_url(self):
        # 将消息传递给下一次请求
        messages.success(self.request, self.message)
        return reverse_lazy('articles:list')


def notify_comment(**kwargs):
    """文章新增评论时通知作者"""
    actor = kwargs['request'].user  # kwargs['request']提交的HttpRequest
    # kwargs['comment']提交的Comment实例，kwargs['comment'].content_boject 表示Comment关联的通用外键模型类名（即文章对象）
    obj = kwargs['comment'].content_boject
    # 通知文章作者，有新评论了
    notification_handler(actor, obj.user, 'C', obj)


comment_was_posted.connect(receiver=notify_comment)  # 使用信号量
