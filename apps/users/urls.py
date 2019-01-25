# _*_ coding: utf-8 _*_

# _Author_: 'Anson'

# _Time_: '2019-01-13 13:07'

from django.urls import path, re_path

from .views import UserInfoView, ImageUploadView, UpdatePwdView, SendEmailCodeView, UpdateEmailView, MyCourseView
from .views import MyFavOrgView, MyFavTeacherView, MyFavCourseView, MyMessageView

app_name = '[users]'
urlpatterns = [
    path('info/', UserInfoView.as_view(), name='user_info'),
    path('image/upload/', ImageUploadView.as_view(), name='image_upload'),
    path('update/pwd/', UpdatePwdView.as_view(), name='update_pwd'),
    path('sendemail_code/', SendEmailCodeView.as_view(), name='sendemail_code'),
    path('update_email/', UpdateEmailView.as_view(), name='update_email'),
    path('my_course/', MyCourseView.as_view(), name='my_course'),
    path('my_fav/org/', MyFavOrgView.as_view(), name='fav_org'),
    path('my_fav/teacher/', MyFavTeacherView.as_view(), name='fav_teacher'),
    path('my_fav/course/', MyFavCourseView.as_view(), name='fav_course'),
    path('my_message/', MyMessageView.as_view(), name='my_message'),


]
