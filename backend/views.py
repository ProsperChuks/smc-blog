import smtplib, ssl
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from .models import *
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

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


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

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
            subscribers_queryset = [mail.email for mail in subscribedUsers.objects.all()]
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
        serializer = commentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
