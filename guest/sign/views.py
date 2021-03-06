from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event,Guest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.

#打开首页
def index(request):
    return render(request,"index.html")

#登录
def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user) #登录
            request.session['user'] = username #将session信息记录到浏览器
            response = HttpResponseRedirect('/event_manage/')
            return response

        else:
            return render(request,'index.html',{'error':'username or password error!'})

#发布会管理
@login_required #必须通过登录才能访问发布会管理页面
def event_manage(request):
    event_list = Event.objects.all()
    username = request.session.get('user','') #读取浏览器session
    return render(request,"event_manage.html",{"user":username,"events":event_list})


#发布会名称搜索
@login_required #必须通过登录才能访问发布会管理页面
def search_name(request):
    username = request.session.get('user','') #读取浏览器session
    search_name = request.GET.get("name","")
    events = Event.objects.filter(name__contains=search_name)
    if len(events) == 0:
        return render(request, "event_manage.html", {"user": username,
                                                     "hint": "根据输入的 `发布会名称` 查询结果为空！"})
    return render(request, "event_manage.html", {"user": username, "events": events})


#嘉宾管理
@login_required
def guest_manage(request):
    username = request.session.get('user', '')
    guest_list = Guest.objects.all()
    paginator = Paginator(guest_list,2)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # 如果页数不是整型, 取第一页.
        contacts = paginator.page(1)
    except EmptyPage:
        # 如果页数超出查询范围，取最后一页
        contacts = paginator.page(paginator.num_pages)
    return render(request, "guest_manage.html", {"user": username, "guests": contacts})

#签到页面
@login_required
def sign_index(request,eid):
    event = get_object_or_404(Event,id=eid)
    return render(request,"sign_index.html",{"event":event})


# 签到动作
@login_required
def sign_index_action(request,eid):
    event = get_object_or_404(Event, id=eid)
    phone =  request.POST.get('phone','')
    print(phone)
    result = Guest.objects.filter(phone = phone)

    if not result:
        return render(request, 'sign_index.html', {'event': event,'hint': 'phone error.'})

    result = Guest.objects.filter(phone = phone,event_id = eid)
    if not result:
        return render(request, 'sign_index.html', {'event': event,'hint': 'event id or phone error.'})

    result = Guest.objects.get(event_id = eid,phone = phone)

    if result.sign:
        return render(request, 'sign_index.html', {'event': event,'hint': "user has sign in."})
    else:
        Guest.objects.filter(event_id = eid,phone = phone).update(sign = '1')
        return render(request, 'sign_index.html', {'event': event,'hint':'sign in success!', 'guest':result})


#退出系统
@login_required
def logout(request):
    auth.logout(request)
    response = HttpResponseRedirect('/index/')
    return response

