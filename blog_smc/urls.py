"""blog_smc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from backend import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.decorators.cache import never_cache
from ckeditor_uploader import views as ckeditor_views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'groups', views.GroupViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'posts', views.postViewSet, basename='posts')
router.register(r'images', views.imageViewSet)
router.register(r'videos', views.VideoViewSet)
router.register(r'post/review', views.postReviewViewSet)
router.register(r'subscribe', views.postSubscribe)
router.register(r'comment', views.CommentViewSet, basename='comment-detail')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('allauth.urls')),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path(r'ckeditor/upload/', ckeditor_views.upload, name='ckeditor_upload'),
    path(r'ckeditor/browse/', never_cache(ckeditor_views.browse), name='ckeditor_browse'),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
