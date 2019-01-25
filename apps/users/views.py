import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .forms import RegisterForm, LoginForm,ForgetForm,ModifyPwdForm, UserInfoForm
from .models import UserProfile, EmailVerifyRecord, Banner
from operation.models import UserCourse, UserFavorite, UserMessage
from organization.models import CourseOrg, Teacher
from courses.models import Course
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from .forms import UploadImageForm
# Create your views here.


class CustomBackend(ModelBackend):
        # 重写authenticate验证方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
            return render(request, 'login.html')
        else:
            return render(request, "active_fail.html")


class ResetPwdView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email

                return render(request, 'password_reset.html', {"email": email})
        else:
            return render(request, "active_fail.html")


class ModifyPwdView(View):
    def post(self,request):
        modify_pwd = ModifyPwdForm(request.POST)
        if modify_pwd.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            if pwd1 != pwd2:
                print(pwd1)
                print(pwd2)
                return render(request, 'password_reset.html', {"email": email, "msg": "两次密码不一致！"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd1)
            user.save()
            return render(request, "login.html")
        else:
            email = request.POST.get("email", "")
            return render(request, 'password_reset.html', {"email": email, "modify_pwd": modify_pwd})


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm(request.POST)
        return render(request, "register.html", {"register_form": register_form})

    def post(self,request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get("email", "")
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "用户名已经存在！"})
            else:
                pass_word = request.POST.get("password", "")
                user_profile = UserProfile()
                user_profile.is_active = False
                user_profile.username = user_name
                user_profile.email = user_name
                user_profile.password = make_password(pass_word)
                user_profile.save()

                user_message = UserMessage()
                user_message.user = user_profile.id
                user_message.message = "欢迎注册！"
                user_message.save()

                send_register_email(user_name, "register")

                return render(request, "login.html", {})
        else:
            return render(request, "register.html", {"register_form": register_form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("index"))


class LoginView(View):
    def get(self,request):
        return render(request, "login.html", {})

    def post(self,request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "login.html", {"msg": "用户未激活！"})
            else:
                return render(request, "login.html", {"msg": "用户名或者密码错误！"})
        else:
            return render(request, "login.html", {"login_form": login_form})


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm(request.POST)
        return render(request, "forgetpwd.html", {"forget_form": forget_form})

    def post(self,request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            user_name = request.POST.get("email", "")
            send_register_email(user_name, "forget")
            return render(request, "send_success.html")
        else:
            return render(request, "forgetpwd.html", {"forget_form": forget_form})


class UserInfoView(LoginRequiredMixin, View):
    def get(self,request):
        return render(request, 'usercenter-info.html', {
        })

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class ImageUploadView(LoginRequiredMixin, View):

    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return HttpResponse('{"status":"success",}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail",}', content_type='application/json')


class UpdatePwdView(View):
    def post(self, request):
        modify_pwd = ModifyPwdForm(request.POST)
        if modify_pwd.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                print(pwd1)
                print(pwd2)
                return HttpResponse('{"status":"fail","msg": "密码不一致!"}', content_type='application/json')
            user = UserProfile.objects.get(id=int(request.user.id))
            user.password = make_password(pwd1)
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_pwd.errors), content_type='application/json')


class SendEmailCodeView(View):
    def get(self, request):
        email = request.GET.get("email", "")
        print(email)
        if UserProfile.objects.filter(email=email):
            print("错了")
            return HttpResponse('{"email": "该邮箱已经存在！"}', content_type='application/json')
        else:
            print("对了")
            send_register_email(email=email, send_type="update_email")
            return HttpResponse('{"status": "success"}', content_type='application/json')


class UpdateEmailView(View):
    def post(self, request):
        email = request.POST.get("email", "")
        code = request.POST.get("code", "")
        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type="update_email")
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"email": "验证码错误！"}', content_type='application/json')


class MyCourseView(View):
    def get(self, request):
        my_courses = UserCourse.objects.filter(user=request.user)

        return render(request, 'usercenter-mycourse.html', {
            'my_courses': my_courses,
        })


class MyFavOrgView(View):
    def get(self, request):
        org_list =[]
        fav_org = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for org in fav_org:
            org_id = org.fav_id
            course_org = CourseOrg.objects.get(id=org_id)
            org_list.append(course_org)

        return render(request, 'usercenter-fav-org.html', {
            'org_list': org_list,
        })


class MyFavTeacherView(View):
    def get(self, request):
        teacher_list =[]
        fav_teacher = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for teacher in fav_teacher:
            teacher_id = teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)

        return render(request, 'usercenter-fav-teacher.html', {
            'teacher_list': teacher_list,
        })


class MyFavCourseView(View):
    def get(self, request):
        course_list =[]
        fav_course = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for course in fav_course:
            course_id = course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)

        return render(request, 'usercenter-fav-course.html', {
            'course_list': course_list,
        })


class MyMessageView(View):
    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id)
        # 清空未读消息
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()

        # 用分页插件进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_messages, per_page=3, request=request)

        messages = p.page(page)
        return render(request, 'usercenter-message.html', {
            'all_messages': messages,
        })


class IndexView(View):
    # 慕学在线网 首页
    def get(self, request):
        # 取出轮播图
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False)[:6]
        print(courses)
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs
        })


def page_not_found(request):
    # 全局404处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    # 全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response

# def user_login(request):
#     if request.method == "POST":
#         user_name = request.POST.get("username", "")
#         pass_word = request.POST.get("password", "")
#         user = authenticate(username=user_name, password=pass_word)
#         if user is not None:
#             login(request, user)
#             return render(request, "index.html", {})
#         else:
#             return render(request, "login.html", {"msg": "用户名或者密码错误！"})
#     elif request.method == "GET":
#         return render(request, "login.html", {})