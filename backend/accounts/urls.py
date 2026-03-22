from django.urls import path
from accounts.views.auth_views import RegisterView, LoginView
from accounts.views.profile_views import ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),

    # NEW
    path('profile/', ProfileView.as_view()),
]