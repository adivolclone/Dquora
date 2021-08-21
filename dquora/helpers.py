from functools import wraps

from django.http import HttpResponseBadRequest
from django.views.generic import View
from django.core.exceptions import PermissionDenied


def ajax_required(f):
    """验证是否为AJAX请求"""

    @wraps(f)
    def wrap(request, *args, **kwargs):
        # request.is_ajax() 这个是request的一个方法，判断是否为AJAX请求
        if not request.is_ajax():
            return HttpResponseBadRequest("不是AJAX请求！")
        return f(request, *args, **kwargs)

    return wrap


class AuthorRequiredMixin(View):
    """
    验证是否为原作者，用于状态删除、文章编辑
    需要重写dispathc方法，不是原作者就不分配处理http请求的方法了
    """

    def dispatch(self, request, *args, **kwargs):
        # 状态和文章实例的user属性
        if self.get_object().user.username != self.request.user.username:
            raise PermissionDenied
        return super(AuthorRequiredMixin, self).dispatch(request, *args, **kwargs)

