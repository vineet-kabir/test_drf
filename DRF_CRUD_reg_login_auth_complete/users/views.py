from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from django.contrib import auth

from django.contrib.auth import login as django_login, logout as django_logout
from rest_framework.authentication import TokenAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authtoken.models import Token

# Create your views here.
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Profile, UserConfirmation
from users.utils import Register, AuthenticationToken

# start registerAPI #
class registerAPI(APIView):

    """
    User register api
    """
    authentication_classes = ()
    permission_classes = ()

    def post(self,request):
        email =request.data.get('email')
        password =request.data.get('password')
        fname =request.data.get('first_name')
        lname =request.data.get('last_name')
        if email and password and fname and lname:
            try:
                user = Profile.objects.get(email=email.strip().lower())
            except ObjectDoesNotExist as e:
                user =None
            if not user:
                    new_user =Register().register1(email,password,fname,lname)
                    return Response(data=[{"data":"A verification email has been sent on "+email}] ,status=status.HTTP_200_OK)

            else:
                    return Response(data=[{"message":"This email is already registred"}],status=status.HTTP_400_BAD_REQUEST)
# end registerAPI #                    

# start verifyemail #
class verifyemail(APIView):
    """
    Verify email Api
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self,request,email,token):
        email = email
        token = token
        user = Profile.objects.get(email = email.strip().lower())

        confirm_user = UserConfirmation.objects.get(user_id=user.id)
        if confirm_user.token==token:
            user.is_verified =True
            user.save()
            return Response(data=[{"message":"Congratulations ! Your account has been verified"}],status=status.HTTP_200_OK)
        else:
            return Response(data=[{"message":"BAD request"}],status=status.HTTP_400_BAD_REQUEST)
# end verifyemail #

# start user_login #
class user_login(APIView):
    """
    Api to login user
    """
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self,request):
        email = request.data.get('email')
        # username = request.data.get('email')
        password = request.data.get('password')

        if email and password:
            try:
                userobj = Profile.objects.get(email=email.strip().lower())
            except ObjectDoesNotExist as e:
                userobj =None
            if userobj:
                if userobj.is_verified:
                    user = authenticate(username=userobj.username, password=password)
                    # django_login(request,user)
                    if user:
                         token, is_created = Token.objects.get_or_create(user=user)
                         return Response(data=[{"token":token.key    ,"message":"login successfully"}],status=status.HTTP_200_OK)
                    else:
                        return Response(data=[{"message":"Email password combination failed"}],status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response(data=[{"message":"This Email has not been verified yet"}],status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(data=[{"message":"Email password combination failed"}],status=status.HTTP_400_BAD_REQUEST)
        else:
                return Response(data=[{"message":"Bad request"}],status=status.HTTP_400_BAD_REQUEST)
# end user_login #

# start user_logout #
class user_logout(APIView):
    """
    Invalidate token
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def post(self, request):
        # request.user.token.delete()
        django_logout(request)
        return Response(data={"message": "logout successfully"}, status=status.HTTP_204_NO_CONTENT)
# end user_logout #

# start Changepassword #
class Changepassword(APIView):
    """
    Api to change logged in user password
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)
    def post(self,request):
        token =request.data.get("token")
        new_password = request.data.get("new_password")
        try:
            userobj = Token.objects.get(key=token).user
        except ObjectDoesNotExist as e:
            userobj =None
        if userobj:
            userobj = Profile.objects.get(email =userobj.email)
            userobj.set_password(new_password)
            userobj.save()
            return Response(data={"message":"Your password has been changed successfully"},status=status.HTTP_200_OK)
        else:
            return Response(data={"message":"Invalid token"},status=status.HTTP_400_BAD_REQUEST)
# end Changepassword #