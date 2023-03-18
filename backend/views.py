import smtplib, ssl
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from .models import *
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings

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

        queryset = post.objects.all()
        category = self.request.query_params.get('category')
        editor = self.request.query_params.get('editor')
        user = self.request.query_params.get('user')
        if user is not None:
            queryset = queryset.filter(author=user)
        if category is not None:
            queryset = queryset.filter(categories__exact=category)
        if editor is not None:
            queryset = queryset.filter(picked__exact=editor)
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
            email = request.POST.get('email')
            PORT = 465
            smtp_server = 'smtp.gmail.com'
            sender_email = 'devhive217@gmail.com'
            password = 'dev31997'
            subject = 'NewsLetter Subscription'
            message = '''From: From <noreply@blogsmc.com>
            Subject: NewsLetter Subscription
            
            Thanks for subscribing to our Newsletter. 
            
            You will get notification of latest articles posted on our website. Please do not reply on this email.
            '''
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email, ]
            # send_mail(subject, message, email_from, recipient_list, fail_silently=False)

            # context = ssl.create_default_context()
            # with smtplib.SMTP_SSL(smtp_server, PORT) as server:
            #     # server.starttls(context=context)
            #     # server.ehlo()  # Can be omitted
            #     server.login(sender_email, password)
            #     server.sendmail(email_from, recipient_list, message)
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
