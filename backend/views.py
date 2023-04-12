import smtplib
import ssl
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from .models import *
from rest_framework import viewsets, generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework import status
from .serializers import *
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from django.conf import settings
import json


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    lookup_field = 'slug'

    def get_queryset(self):

        queryset = User.objects.all()
        user = self.request.query_params.get('email')
        if user is not None:
            queryset = queryset.filter(email=user)
        return queryset


class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = [permissions.IsAuthenticated, ]
    authentication_classes = (TokenAuthentication,)

    def get_object(self, queryset=None):
        user_id = Token.objects.get(key=self.request.auth.key).user
        obj = User.objects.get(name=user_id)
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (TokenAuthentication,)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class postViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = post.objects.all().order_by('-publishedAt')
    serializer_class = postSerializer
    lookup_field = 'slug'
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):

        queryset = post.objects.all().order_by('-publishedAt')
        category = self.request.query_params.get('category')
        editor = self.request.query_params.get('editor')
        user = self.request.query_params.get('user')
        name = self.request.query_params.get('name')
        if user is not None:
            queryset = queryset.filter(author=user)
        if category is not None:
            queryset = queryset.filter(categories__exact=category)
        if editor is not None:
            queryset = queryset.filter(picked__exact=editor)
        if name is not None:
            queryset = queryset.filter(title__icontains=name)
        return queryset

    def create(self, request):
        serializer = postSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            subscribers_queryset = [
                mail.email for mail in subscribedUsers.objects.all()]
            PORT = 465
            smtp_server = 'smtp.mail.yahoo.com'
            login = 'pchukwudi36@yahoo.com'
            password = 'yttwsfqiqjtkymlu'
            email_from = 'pchukwudi36@yahoo.com'
            recipient_list = subscribers_queryset

            text = f"""
            <h3>{request.data["title"]}</h3><br>
            <img src="{request.data["mainImage"]}" alt="Poster">
            <br>
            <p>{request.data["summary"]}</p>
            <a href='#'>Read More</a>"""

            message = EmailMessage()
            message['From'] = 'pchukwudi36@yahoo.com'
            message['Subject'] = f'New Blog Post: {request.data["title"]}'
            message['Date'] = formatdate(localtime=True)
            message['Message-ID'] = make_msgid()
            message.set_content(text, subtype='html')

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, PORT) as server:
                server.set_debuglevel(1)
                server.ehlo()
                server.login(login, password)
                server.send_message(message, email_from, recipient_list)
                server.quit()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class imageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = imageShow.objects.all()
    serializer_class = imageSerializer
    # lookup_field = 'image_slide'


class postReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = postReview.objects.all()
    serializer_class = postReviewSerializer
    # lookup_field = 'slug'
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):

        queryset = postReview.objects.all()
        state = self.request.query_params.get('state')
        if state is not None:
            queryset = queryset.filter(review__exact=state)
        return queryset


class postSubscribe(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = subscribedUsers.objects.all()
    serializer_class = subscribeSerializer

    def create(self, request):
        serializer = subscribeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = request.data['email']
            PORT = 465
            smtp_server = 'smtp.mail.yahoo.com'
            login = 'pchukwudi36@yahoo.com'
            password = 'yttwsfqiqjtkymlu'
            email_from = 'pchukwudi36@yahoo.com'
            recipient_list = [email, ]
            print(email)

            text = """Thanks for subscribing to our Newsletter. \nYou will get notification of latest articles posted on our website. Please do not reply on this email."""

            message = EmailMessage()
            message['From'] = 'pchukwudi36@yahoo.com'
            message['To'] = f'{email}'
            message['Subject'] = 'NewsLetter Subscription'
            message['Date'] = formatdate(localtime=True)
            message['Message-ID'] = make_msgid()
            message.set_content(text)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, PORT) as server:
                server.set_debuglevel(1)
                server.ehlo()
                server.login(login, password)
                server.send_message(message, email_from, recipient_list)
                server.quit()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = comment.objects.all().order_by('-created_on')
    serializer_class = commentSerializer

    def get_queryset(self):

        queryset = comment.objects.all().order_by('-created_on')
        post = self.request.query_params.get('post')
        if post is not None:
            queryset = queryset.filter(post__exact=post)
        return queryset

    def create(self, request):
        serializer = commentSerializer(
            data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CoinIndexViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows price index marquee to be viewed or edited.
    """
    queryset = CoinIndex.objects.all()
    serializer_class = coinIndexSerializer

    def list(self, request, *args, **kwargs):
        coin_index = CoinIndex.objects.first()
        serializer = self.get_serializer(coin_index)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        coin_index, created = CoinIndex.objects.get_or_create(pk=1)
        coin_ids = request.data.get('coin_ids', [])
        for coin_id in coin_ids:
            coin_index.add_coin_id(coin_id)
        serializer = self.get_serializer(coin_index)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        coin_id = kwargs.get('pk')
        coin_index = CoinIndex.objects.first()
        if coin_id is not None and coin_id.isdigit():
            coin_index.remove_coin_id(int(coin_id))
        serializer = self.get_serializer(coin_index)
        return Response(serializer.data)


@api_view(['GET'])
def get_cryptocurrency_map(request):
    start = request.query_params.get('start') or '1'
    limit = request.query_params.get('limit') or '500'
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
    parameters = {
        'start': start,
        'limit': limit,
        'aux': 'is_active'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': settings.CMC_API_KEY,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        return Response(data)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return Response({"error": "Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_cryptocurrency_listings(request):
    start = request.query_params.get('start') or '1'
    limit = request.query_params.get('limit') or '500'
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': start,
        'limit': limit,
        'aux': 'is_active',
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': settings.CMC_API_KEY,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        return Response(data)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return Response({"error": "Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_cryptocurrency_quotes(request):
    url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    parameters = {
        'aux': 'is_active',
        'id': request.query_params.get('id') or '1,20700,23241,1027,74,5426,1839'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': settings.CMC_API_KEY,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        return Response(data)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        return Response({"error": "Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
