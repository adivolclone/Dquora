$(function () {
    const emptyMessage = '没有未读通知';
    const notice = $('#notifications');

    function CheckNotifications() {
        $.ajax({
            url: '/notifications/latest-notifications/',
            cache: false,
            success: function (data) {
                // 有未读通知，把铃铛变为红色
                if (!data.includes(emptyMessage)) {
                    notice.addClass('btn-danger');
                }
            },
        });
    }

    CheckNotifications();  // 页面加载时执行
    // 收到WS的数据后，若是social_update则获取该条动态的赞和评论数据 最新值
    function update_social_activity(id_value) {
        const newsToUpdate = $('[news-id=' + id_value + ']');
        $.ajax({
            url: '/news/update-interactions/',
            data: {'id_value': id_value},
            type: 'POST',
            cache: false,
            success: function (data) {
                $(".like-count", newsToUpdate).text(data.likes);
                $(".comment-count", newsToUpdate).text(data.comments);
            },
        });
    }

    // 通知铃铛的 点击事件
    notice.click(function () {
        // 已经显示了铃铛弹出框，所以再次点击后就 取消显示并更新是否有新的的未读通知
        if ($('.popover').is(':visible')) {
            notice.popover('hide');
            CheckNotifications();
        } else {
            // 第一次点击铃铛，显示通知弹出框
            notice.popover('dispose');
            $.ajax({
                url: '/notifications/latest-notifications/',
                cache: false,
                success: function (data) {
                    // 获取最近未读通知，然后把数据 data 添加到弹出框内
                    notice.popover({
                        html: true,
                        trigger: 'focus',
                        container: 'body',
                        placement: 'bottom',
                        content: data,
                    });
                    // 显示弹出框，并把铃铛变为白色
                    notice.popover('show');
                    notice.removeClass('btn-danger')
                },
            });
        }
        return false;  // 不是False
    });

    // WebSocket连接，使用wss(https)或者ws(http)
    // 协议
    const ws_scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    // WS的routing ws_url路径
    const ws_path = ws_scheme + '://' + window.location.host + '/ws/notifications/';
    // 创建WS实例
    const ws = new ReconnectingWebSocket(ws_path);

    // 监听后端发送过来的消息
    ws.onmessage = function (event) {
        // event.data 后端WebSocket 返回的数据，定义在视图的 payload字典 里
        const data = JSON.parse(event.data);
        // 通过关键字key 判断是那种通知
        switch (data.key) {
            case "notification":
                if (currentUser !== data.actor_name) {  // 消息提示的发起者不提示
                    notice.addClass('btn-danger');
                }
                break;
            // 给动态点赞或评论
            case "social_update":
                if (currentUser !== data.actor_name) {
                    notice.addClass('btn-danger');
                }
                update_social_activity(data.id_value);
                break;
            // 发表新动态
            case "additional_news":
                if (currentUser !== data.actor_name) {
                    $('.stream-update').show();
                }
                break;

            default:
                console.log('error', data);
                break;
        }
    };
});
