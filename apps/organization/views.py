from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q

from .models import CourseOrg, CityDict, Teacher
from .forms import UserAskForm
from operation.models import UserFavorite
from courses.models import Course


# Create your views here.


class OrgView(View):
    def get(self, request):

        all_orgs = CourseOrg.objects.all()
        all_citys = CityDict.objects.all()
        hot_orgs = all_orgs.order_by('click_nums')[:3]

        #机构搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) |Q(desc__icontains=search_keywords))

        # 城市筛选
        city_id = request.GET.get('city', "")
        print(city_id)
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))
            print(all_orgs)
        # 类别筛选
        category = request.GET.get('ct', "")
        if category:
            all_orgs = all_orgs.filter(category=category)
            print(all_orgs)
        # 排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "students":
                all_orgs = all_orgs.order_by("-students")
            elif sort == "courses":
                all_orgs = all_orgs.order_by("-course_nums")

        org_nums = all_orgs.count()

        # 用分页插件进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        # objects = ['john', 'edward', 'josh', 'frank']

        # Provide Paginator with the request object for complete querystring generation

        p = Paginator(all_orgs, per_page=5, request=request)

        orgs = p.page(page)

        return render(request, 'org-list.html', {
            'all_orgs': orgs,
            'all_citys': all_citys,
            'org_nums': org_nums,
            'city_id': city_id,
            'category': category,
            'hot_orgs': hot_orgs,
            'sort': sort,
        })


class AddUserAskView(View):
    """
    用户添加咨询
    """
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


class OrgHomeView(View):
    """
    机构首页
    """

    def get(self, request, org_id):
        current_page = "home"
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1
        course_org.save()
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()[:3]
        all_teachers = course_org.teacher_set.all()[:1]

        return render(request, 'org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teachers': all_teachers,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav
        })


class OrgCourseView(View):
    """
    机构课程
    """

    def get(self, request, org_id):
        current_page = "course"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_courses = course_org.course_set.all()

        return render(request, 'org-detail-course.html', {
            'all_courses': all_courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgDescView(View):
    """
    机构介绍
    """

    def get(self, request, org_id):
        current_page = "desc"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class OrgTeacherView(View):
    """
    机构教师
    """

    def get(self, request, org_id):
        current_page = "teacher"
        course_org = CourseOrg.objects.get(id=int(org_id))
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True
        all_teacher = course_org.teacher_set.all()

        return render(request, 'org-detail-teachers.html', {
            'all_teacher': all_teacher,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


class AddFavView(View):
    """
    用户收藏
    """

    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)

        # 判断用户是否登录
        if not request.user.is_authenticated:
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        else:
            exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
            print(exist_records)
            if exist_records:
                # 如果记录存在，则表示用户取消收藏
                exist_records.delete()
                # 收藏数
                if int(fav_type) == 1:
                    course = Course.objects.get(id=fav_id)
                    course.fav_nums -= 1
                    if course.fav_nums < 0:
                        course.fav_nums = 0
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=fav_id)
                    course_org.fav_nums -= 1
                    if course_org.fav_nums < 0:
                        course_org.fav_nums = 0
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=fav_id)
                    teacher.fav_nums -= 1
                    if teacher.fav_nums < 0:
                        teacher.fav_nums = 0
                    teacher.save()
                return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')
            else:
                user_fav = UserFavorite()
                print(int(fav_id))
                print(int(fav_type))
                if int(fav_id) > 0 and int(fav_type) > 0:
                    user_fav.user = request.user
                    user_fav.fav_id = int(fav_id)
                    user_fav.fav_type = int(fav_type)
                    user_fav.save()
                    # 收藏数
                    if int(fav_type) == 1:
                        course = Course.objects.get(id=fav_id)
                        course.fav_nums += 1

                        course.save()
                    elif int(fav_type) == 2:
                        course_org = CourseOrg.objects.get(id=fav_id)
                        course_org.fav_nums += 1

                        course_org.save()
                    elif int(fav_type) == 3:
                        teacher = Teacher.objects.get(id=fav_id)
                        teacher.fav_nums += 1

                        teacher.save()
                    return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
                else:
                    return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')


class TeacherListView(View):
    def get(self, request):
        all_teachers = Teacher.objects.all()
        # 课程讲师搜索
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_teachers = all_teachers.filter(Q(name__icontains=search_keywords)|
                                               Q(work_company__icontains=search_keywords)|
                                               Q(work_position__icontains=search_keywords))
        hot_teachers = Teacher.objects.all().order_by("-click_nums")[:5]
        # 排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "hot":
                all_teachers = all_teachers.order_by("-click_nums")

        org_nums = all_teachers.count()
        # 用分页插件进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_teachers, per_page=2, request=request)

        teachers = p.page(page)
        return render(request, 'teachers-list.html', {
            'all_teachers': teachers,
            'sort': sort,
            'hot_teachers': hot_teachers,
            'org_nums': org_nums,
        })


class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))
        teacher.click_nums += 1
        teacher.save()
        hot_teachers = Teacher.objects.all().order_by("-click_nums")[:5]
        all_courses = Course.objects.filter(teacher_id=teacher)
        has_fav_teacher = False
        has_fav_org = False
        if UserFavorite.objects.filter(user=request.user, fav_id=teacher.id, fav_type=3):
            has_fav_teacher = True

        if UserFavorite.objects.filter(user=request.user, fav_id=teacher.org.id, fav_type=2):
            has_fav_org = True

        return render(request, 'teacher-detail.html', {
            "teacher": teacher,
            "all_courses": all_courses,
            "hot_teachers": hot_teachers,
            "has_fav_teacher": has_fav_teacher,
            "has_fav_org": has_fav_org,

        })

