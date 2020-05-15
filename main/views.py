from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import User, auth
from django.contrib.auth import get_user_model, authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .detect import main_detect
from .vegetation_localization import veg_localization
import os

User = get_user_model()
# Create your views here.

image_path = []
output_path = []


def index(request):
    if request.method == 'POST':
        name = request.POST['name']
        message = request.POST['message']
        email = request.POST['email']
        contacts = contact.objects.create(name=name, email=email, comment=message)
    return render(request, "index.html")


def signin(request):
    if request.user.is_authenticated:
        return redirect('upload')
    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']
            remember_me = request.POST.get('remember')
            if(remember_me == "on"):
                request.session.set_expiry(600 * 100)

            if User.objects.filter(email=email).exists():
                user = auth.authenticate(email=email, password=password)
                if user is not None:
                    auth.login(request, user)
                    request.session['user_id'] = user.id
                    return redirect('upload')
                else:
                    messages.error(
                        request, "Your password is incorrect. Try again or click forgot password.", extra_tags="password")
                    return HttpResponseRedirect(request.path)
            else:
                messages.error(
                    request, "This email has not been registered. Click signup to register this account.", extra_tags="email")
                return HttpResponseRedirect(request.path)
        else:
            return render(request, "signin.html")


def signup(request):
    if request.method == 'POST':
        fName = request.POST['fname']
        lName = request.POST['lname']
        email = request.POST['email']
        gender = request.POST['gender']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    first_name=fName, last_name=lName, gender=gender, email=email, password=password1)
                user.save()
                return redirect('signin')
        else:
            messages.info(request, 'Password not matching')
            return redirect('signup')

    else:
        return render(request, 'signup.html')


@login_required
def services(request):
    if request.method == 'POST':

        user = User.objects.get(id=request.session['user_id'])
        
        if request.POST.get("Object"):
            return redirect('object_detection')
        elif request.POST.get("land_use"):
            # hist = history.objects.create(user_id=user, time=myDate, pic=image, selection='identify') 
            return redirect('land_use')
        elif request.POST.get("parameter"):
            # hist = history.objects.create(user_id=user, time=myDate, pic=image, selection='other')
            return redirect('parameter')
        elif request.POST.get("vegetation_localization"):
            # hist = history.objects.create(user_id=user, time=myDate, pic=image, selection='other')
            return redirect('vegetation_localization')
    return render(request, "Services.html")


@login_required
def history_view(request):
    user = User.objects.get(id=request.session['user_id'])
    his = history.objects.filter(user_id=user)
    context = {
        'history': his,
    }
    return render(request, "History.html", context)


@login_required
def logout_request(request):
    auth.logout(request)
    return redirect('index')


@login_required
def view_profile(request):
    user = User.objects.get(id=request.session['user_id'])
    context = {
        'user': user,
    }
    return render(request, "view_profile.html", context)


@login_required
def gallery(request):
    user = User.objects.get(id=request.session['user_id'])
    gallery = pics.objects.filter(user_id=user)
    context = {
        'gallery': gallery,
    }
    return render(request, "Gallery.html", context)


@login_required
def upload(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.session['user_id'])
        print('Checking...')
        for img in request.FILES.getlist('media'):
            image = pics.objects.create(user_id=user,image=img)
            image_path.append(image.image.name)
        return redirect('services')
    else:
        return render(request, "upload.html")


@login_required
def update_profile_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        gender = request.POST.get('gender')

        user = User.objects.get(id=request.session['user_id'])

        user.email = email
        user.first_name = fname
        user.last_name = lname
        user.gender = gender
        user.save()
        update_session_auth_hash(request, user)

        return redirect('view_profile')
    else:
        return render(request, 'Edit_Profile.html')


@login_required
def change_password_request(request):
    if request.method == 'POST':
        old_password = request.POST.get('Current_Password')
        new_password = request.POST.get('New_Password')
        confirm_password = request.POST.get('Confirm_Password')
        if new_password == confirm_password:
            user = User.objects.get(id=request.session['user_id'])
            exists = auth.authenticate(email=user.email, password=old_password)
            if exists is not None:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                return redirect('upload')
            else:
                messages.error(
                    request, "You've entered a wrong password", extra_tags="password")
                return HttpResponseRedirect(request.path)
        else:
            messages.error(
                request, "New password fields won't match", extra_tags="password")
            return HttpResponseRedirect(request.path)
    else:
        return render(request, 'change_password.html')


@login_required
def object_detection(request):
    myDate = datetime.now()
    user = User.objects.get(id=request.session['user_id'])
    
    output_path.clear()
    
    for img in image_path:
        img_ = settings.BASE_DIR + settings.MEDIA_URL + img
        img_ = img_.replace(os.sep, '/')
        image_name = img.split('/')

        output_file_name, Area, Parameter_width, Parameter_height = main_detect(img_, image_name[1])

        output_path.append(settings.MEDIA_URL + output_file_name)

        images = pics.objects.create(user_id=user,image=output_file_name)
        
        hist = history.objects.create(user_id=user, time=myDate, pic=img, selection='Object Detection')
    image_path.clear()
    
    return render(request, 'object_detection.html', {"output": output_path})


@login_required
def land_use(request):
    myDate = datetime.now()
    user = User.objects.get(id=request.session['user_id'])

    output_path.clear()

    for img in image_path:
        img_ = settings.BASE_DIR + settings.MEDIA_URL + img
        img_ = img_.replace(os.sep, '/')
        image_name = img.split('/')

        output_file_name, Area, Parameter_width, Parameter_height = main_detect(img_, image_name[1])

        output_path.append(settings.MEDIA_URL + output_file_name)
        hist = history.objects.create(user_id=user, time=myDate, pic=img, selection='Land Use')
    image_path.clear()
    
    return render(request, 'area.html', {"Areas": Area})


@login_required
def parameter(request):
    myDate = datetime.now()
    user = User.objects.get(id=request.session['user_id'])

    output_path.clear()

    for img in image_path:
        img_ = settings.BASE_DIR + settings.MEDIA_URL + img
        img_ = img_.replace(os.sep, '/')
        image_name = img.split('/')

        output_file_name, Area, Parameter_width, Parameter_height = main_detect(img_, image_name[1])

        Parameter_width = Parameter_width['field']
        Parameter_height = Parameter_height['field']
    
        output_path.append(settings.MEDIA_URL + output_file_name)
        hist = history.objects.create(user_id=user, time=myDate, pic=img, selection='Crop Parameters')
    
    image_path.clear()
    
    return render(request, 'parameters.html', {"Parameter_width": Parameter_width, "Parameter_height": Parameter_height})


@login_required
def vegetation_localization(request):
    myDate = datetime.now()
    user = User.objects.get(id=request.session['user_id'])
    
    output_path.clear()
    
    for img in image_path:
        img_ = settings.BASE_DIR + settings.MEDIA_URL + img
        img_ = img_.replace(os.sep, '/')
        image_name = img.split('/')

        output_file_name = veg_localization(img_, image_name[1])

        output_path.append(settings.MEDIA_URL + output_file_name)

        images = pics.objects.create(user_id=user,image=output_file_name)
        
        hist = history.objects.create(user_id=user, time=myDate, pic=img, selection='Vegetation Localization')
    image_path.clear()
    
    return render(request, 'vegetation_localization.html', {"output": output_path})