# _*_ coding: utf-8 _*_

# _Author_: 'Anson'

# _Time_: '2019-01-11 13:54'

from django.urls import path, re_path
from .views import CourseListView, CourseDetailView, CourseInfoView, CommentView, AddComentsView


app_name = '[courses]'
urlpatterns = [
    path('list/', CourseListView.as_view(), name='course_list'),
    re_path(r'^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name="course_deail"),
    re_path(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name="course_info"),
    re_path(r'^comment/(?P<course_id>\d+)/$', CommentView.as_view(), name="course_comment"),
    path('add_comment/', AddComentsView.as_view(), name="add_comment"),

]

