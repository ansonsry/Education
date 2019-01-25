# _*_ coding: utf-8 _*_

# _Author_: 'Anson'

# _Time_: '2019-01-10 19:41'


from django.urls import path, include, re_path
from django.conf.urls import url

from organization.views import OrgView, AddUserAskView, OrgHomeView, OrgCourseView, OrgDescView, OrgTeacherView
from organization.views import AddFavView, TeacherListView, TeacherDetailView

app_name = '[organization]'
urlpatterns = [

    # 课程机构URL
    path('org_list/', OrgView.as_view(), name="org_list"),
    path('add_ask/', AddUserAskView.as_view(), name="add_ask"),
    re_path(r'^home/(?P<org_id>\d+)/$', OrgHomeView.as_view(), name="org_home"),
    re_path(r'^course/(?P<org_id>\d+)/$', OrgCourseView.as_view(), name="org_course"),
    re_path(r'^desc/(?P<org_id>\d+)/$', OrgDescView.as_view(), name="org_desc"),
    re_path(r'^org_teacher/(?P<org_id>\d+)/$', OrgTeacherView.as_view(), name="org_teacher"),
    # 收藏
    path('add_fav/', AddFavView.as_view(), name="add_fav"),
    # 讲师列表
    path('teacher_list/', TeacherListView.as_view(), name="teacher_list"),
    re_path(r'^teacher_detail/(?P<teacher_id>\d+)/$', TeacherDetailView.as_view(), name="teacher_detail"),

]