from django.urls import path
from .views import user_register, user_login, home, user_logout, root, user_profile, create_appeal, news, see_map, \
    appeals, create_news, answer_appeals

urlpatterns = [
    path('', root, name=''),
    path('profile/', user_profile, name='user_profile'),
    path('register/', user_register, name='user_register'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('home/', home, name='home'),
    path('news/', news, name='news'),
    path('map/', see_map, name='map'),
    path('appeals', appeals, name='appeals'),
    path('answer_appeals', answer_appeals, name='answer_appeals'),
    path('create_appeal/', create_appeal, name='create_appeal'),
    path('create_news/', create_news, name='create_news'),

]
