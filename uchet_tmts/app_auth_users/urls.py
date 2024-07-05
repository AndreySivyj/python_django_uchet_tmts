from django.urls import path, include
from .views import *
from laptop.views import reestr_tmts_list_view


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', include('laptop.urls')), # главная страница, в т.ч. LOGIN_REDIRECT_URL
    # path('reestr_tmts_list/', reestr_tmts_list_view, name='reestr_tmts_list'),
    # path('login/', AnotherLoginView.as_view(), name='login'),
]

