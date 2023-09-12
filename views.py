from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from rango.models import Category,Page
from rango.forms import CategoryForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
    request.session.set_test_cookie()
    context_list = Category.objects.all()
    page_list = Page.objects.all()
    context_dict = {'categorys':context_list, 'pages': page_list}
    #context_dict = {'boldmessage':"赵"}
    #response = render(request, 'rango/index.html', context_dict)
    
    #visitor_cookie_handler(request,response)
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context=context_dict)
    
    #return render(request,'rango/index.html',context_dict)
    return response
    
def about(request):
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    return HttpResponse("说明 <br/><a href ='/rango'>首页</a>")


def show_category(request,category_name_slug):
    context_dict = {}
    try:
        category = category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category= category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
    return render(request,'rango/category.html', context_dict)
    


def add_category(request):
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    return render(request,'rango/add_category.html', {'form':form})


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(data = request.POST)
        profile_form = UserProfileForm(data=request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request,
                  'rango/register.html',
                  {'user_form':user_form,
                  'profile_form':profile_form,
                  'registered':registered}
                  )
    
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("您的账户还没有激活")
        else:
            print("用户名或密码无效:{0},{1}".format(username,password))
            return HttpResponse("无效登录信息")
    else:
        return render(request, 'rango/login.html',{})
    
    
@login_required
def restricted(request):
    return HttpResponse("您已授权登录，可以查阅")

def user_logout(request):
    logout(request)
    
    return HttpResponseRedirect(reverse('index'))


def get_server_side_cookie(request, cookie,default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):  #v如果会话在客户端，需添加resposne
    
    #visits = int(request.COOKIES.get('visits',1))  #客户端
    visits = int(get_server_side_cookie(request,'visits','1'))
    #last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
    last_visit_cookie = get_server_side_cookie(request,'last_visit', str(datetime.now())
                                               )
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')
    
    if (datetime.now()-last_visit_time).seconds>0:
        visits = visits +1
        #response.set_cookie('last_visit',str(datetime.now()))
        request.session['last_visit'] = str(datetime.now())
    else:
        #response.set_cookie('last_visit',last_visit_cookie)
        request.session['last_visit'] = last_visit_cookie
        
    #response.set_cookie('visits',visits)
    request.session['visits'] = visits
    

        
        
        
        
    
    