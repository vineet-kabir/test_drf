from django.urls import path, include

from users.views import registerAPI, verifyemail, user_login, user_logout, Changepassword

urlpatterns = [
    path('register/',registerAPI.as_view(),name='registration' ),
    path('verify-email<str:email>/token<str:token>/',verifyemail.as_view(),name = 'verify-email'),
    path('login/',user_login.as_view(),name = 'login'),
    path('logout/',user_logout.as_view(),name = 'logout'),
    path('Change-password/',Changepassword.as_view(),name = 'Changepassword'),
 ]
