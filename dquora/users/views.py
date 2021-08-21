from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, UpdateView
from django.urls import reverse

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    template_name = "users/user_detail.html"
    # model里包含slug的字段，通常是username
    slug_field = "username"
    # url中包含slug（username）的key-value关键字参数
    slug_url_kwarg = "username"


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):

    model = User
    template_name = "users/user_form.html"
    fields = ["nickname","job_title","introduction","picture","location","personal_url","weibo","zhihu","github","linkedin"]
    success_message = _("Information successfully updated")

    # 更新成功后调整的页面
    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    # 获取需要返回给前端的对象，返回当前登录用户的数据
    def get_object(self):
        return self.request.user




