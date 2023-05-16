from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import AdvList, AdvDetail, RegistrationView, confirm_emal, AdvCreate, AdvUpdate, AdvDelete, delete_file, UserAdvReplys


urlpatterns = [
    path('', AdvList.as_view()),
    path('<int:pk>', AdvDetail.as_view()),
    path('login/', LoginView.as_view(template_name='account/login.html')),
    path('logout/', LogoutView.as_view(template_name='account/logout.html')),
    path('signup/', RegistrationView.as_view()),
    path('confirmEmail/', confirm_emal, name='confirm_emal'),
    path('advCreate/', AdvCreate.as_view()),
    path('<int:pk>/edit/', AdvUpdate.as_view()),
    path('<int:pk>/delete/', AdvDelete.as_view()),
    path('<int:pk>/delete_file/', delete_file, name='delete_file'),
    path('advSearch/', UserAdvReplys.as_view()),
]
