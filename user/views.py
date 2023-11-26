import math

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from .forms import CustomUserCreationForm, LoginForm, CreateAppealForm, CreateNewsForm, ProfileEditForm, NewsFilterForm, \
    AnswerAppealForm
from .models import Appeal, Photo, City, News, AppealAnswer, Position


def user_register(request):
    if request.user.is_authenticated:
        return redirect('')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'auth/register.html', {'form': form, 'user': request.user})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, 'Invalid login credentials.')
    else:
        form = LoginForm()

    return render(request, 'auth/login.html', {'form': form, 'user': request.user})


def root(request):
    return redirect('home')


def home(request: WSGIRequest):
    user = request.user
    news = News.objects.filter(city=user.city if user.is_authenticated else 1).order_by('-publication_date')

    return render(request, 'main/home.html', context={'user': user, 'news': news})


def user_profile(request: WSGIRequest):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ProfileEditForm(request.POST)
            if form.is_valid():
                # Обработка данных формы и сохранение в профиле пользователя
                request.user.address_street = form.cleaned_data['address_street']
                request.user.address_house = form.cleaned_data['address_house']
                request.user.save()
                return redirect('user_profile')
        else:
            form = ProfileEditForm(initial={
                'address_street': request.user.address_street,
                'address_house': request.user.address_house
            })
        return render(request, 'main/profile.html', context={'user': request.user, 'form': form})
    else:
        return redirect('user_login')


def news(request: WSGIRequest):
    user = request.user
    if request.method == 'POST':
        form = NewsFilterForm(request.POST)
        if form.is_valid():
            unselected_categories = form.get_not_selected_categories()
        else:
            unselected_categories = []
    else:
        form = NewsFilterForm()
        unselected_categories = request.GET.get('excepts', '').split(',')

    page = request.GET.get('page', 1)
    existing_params = f'&excepts={",".join(unselected_categories)}' if unselected_categories else ''

    news_per_page = 5
    news = News.objects.filter(city=user.city if user.is_authenticated else 1).exclude(
        category__in=unselected_categories).order_by('-publication_date')

    paginator = Paginator(news, news_per_page)

    try:
        current_page = paginator.page(page)
    except PageNotAnInteger:
        current_page = paginator.page(1)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages)
    return render(request, 'main/news.html',
                  context={'user': user, 'news': current_page.object_list, 'current_page': current_page, 'form': form,
                           'existing_params': existing_params})


def see_map(request: WSGIRequest):
    if request.user.is_authenticated:
        return render(request, 'main/map.html', context={'user': request.user})
    else:
        return redirect('user_login')


def appeals(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    appeals = Appeal.objects.filter(user=request.user)
    return render(request, 'main/appeals.html', context={'appeals': appeals, 'user': request.user})


def answer_appeals(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('user_login')

    if request.method == 'POST':
        form = AnswerAppealForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['answer']
            appeal_id = form.cleaned_data['appeal_id']
            appeal = Appeal.objects.get(id=appeal_id)
            position = Position.objects.get(municipality=request.user.municipality, user=request.user)
            ans = AppealAnswer(appeal=appeal, answerer=position, text=answer)
            appeal.is_answered = True
            appeal.save()
            ans.save()

    appeals = Appeal.objects.filter(municipality=user.municipality)
    forms = []
    for i in range(len(appeals)):
        form = AnswerAppealForm(initial={'appeal_id': appeals[i].id})
        forms.append(form)
    zipped = zip(appeals, forms)

    return render(request, 'main/answer_appeals.html', context={'zipped': zipped, 'user': user, })


def create_appeal(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    form = CreateAppealForm()

    if not request.user.is_authenticated:
        return redirect('user_login')
    if request.method == 'POST':
        form = CreateAppealForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
            photo_files = request.FILES.getlist('photos')
            municipality = form.cleaned_data['municipality']
            errors = False
            photos = []
            for photo_file in photo_files:
                photo_instance = Photo(image=photo_file)
                photos.append(photo_instance)
                if not photo_file.content_type.startswith('image'):
                    form.add_error(None, 'Можно передать только фотографии')
                    errors = True

            if not errors:
                appeal = Appeal(title=title, text=text, municipality=municipality, user=request.user)
                appeal.save()
                for photo in photos:
                    photo.save()
                    appeal.photos.add(photo)

                appeal.save()

                return redirect('')
    else:
        return redirect('')

    return render(request, 'create/appeal.html', {'form': form, 'user': request.user})


def create_news(request):
    if not request.user.is_authenticated or request.user.role == 1:
        return redirect('')

    if request.method == 'POST':
        form = CreateNewsForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            short_description = form.cleaned_data['short_description']
            text = form.cleaned_data['text']
            photo_files = request.FILES.getlist('photos')
            municipality = request.user.municipality
            category = form.cleaned_data['category']

            errors = False
            photos = []
            for photo_file in photo_files:
                photo_instance = Photo(image=photo_file)
                photos.append(photo_instance)
                if not photo_file.content_type.startswith('image'):
                    form.add_error(None, 'Можно передать только фотографии')
                    errors = True

            if not errors:
                news = News(title=title, short_description=short_description, text=text, municipality=municipality,
                            author=request.user, category=category)
                news.save()
                for photo in photos:
                    photo.save()
                    news.photos.add(photo)

                news.save()

                return redirect('')
    else:
        form = CreateNewsForm()

    return render(request, 'create/news.html', {'form': form, 'user': request.user})


def user_logout(request: WSGIRequest):
    logout(request)
    return redirect('/')
