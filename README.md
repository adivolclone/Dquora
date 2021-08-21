# Dquora

[![Python](https://img.shields.io/badge/python-3.7.8-blue.svg?style=flat-square)](https://www.python.org/downloads/release/python-378/)
[![Django](https://img.shields.io/badge/django-2.1.7-blue.svg?style=flat-square)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/bootstrap-4.1.1-blue.svg?style=flat-square)](https://getbootstrap.com/docs/4.1/getting-started/introduction/)

> #### 基于 Python 和 Django 的知识问答平台。


## 概览

+ 使用Supervisor进行部署
+ 前端使用DTL，后端模块化编程，前后端不分离
+ 支持动态、问答、发表文章
+ 支持点赞、评论、消息通知
+ 支持Markdown及预览
+ 支持用户间私信

## 安装部署
### Linux 环境

1. 安装必要的依赖及服务

    ```bash
    yum install -y python-devel zlib-devel mysql-devel libffi-devel bzip2-devel openssl-devel java gcc wget
    yum install -y nginx redis supervisor git
    systemctl enable redis nginx supervisord
    ```
2. mysql服务
    ```bash
    systemctl enable mysqld
    create database dquora charset utf8;
    create user 'dquora'@'%' identified by 'dquora123';
    use dquora;
    grant all on dquora to 'dquora'@'%';
    flush privileges;
    ```
3. 包安装
    ```bash
    cd /root/myproject/dquora
    pipenv shell
    mkdir logs
    pip3 install -r deploy/requirements.txt
    python manage.py collectstatic
    python manage.py makemigrations
    python manage.py migrate
    ```
4. 启动服务
    ```bash
    /usr/local/python3/bin/gunicorn --env DJANGO_SETTINGS_MODULE=config.settings.local -b 127.0.0.1:9000 --chdir /root/myproject/dquora config.wsgi
    /usr/local/python3/bin/daphne -p 8000 config.asgi:application
    /usr/local/python3/bin/celery --work=/root/myproject/dquora -A dquora.taskapp worker -l info
    cp deploy/nginx.conf /etc/nginx/nginx.conf
    systemctl restart nginx
    cp deploy/*.ini /etc/supervisord.d/
    systemctl start supervisord
    supervisorctl update
    supervisorctl reload

    ```
## 浏览器支持

Modern browsers(chrome, firefox) 和 Internet Explorer 10+.

## 特别感谢

+ [Echo1996](https://github.com/Ehco1996/django-sspanel)
+ [Dusai](https://github.com/stacklens/django_blog_tutorial)

## 许可

The [MIT](http://opensource.org/licenses/MIT) License

