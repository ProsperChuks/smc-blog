import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify 
from ckeditor.fields import RichTextField
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail 

# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=200, verbose_name='Name', help_text='Name to be displayed under blog posts')
    slug =  models.SlugField(max_length=5500, verbose_name='Slug', unique=True, blank=False, null=False)
    image = models.ImageField(upload_to='author', verbose_name='Image', blank=True, null=True)
    bio = models.TextField(verbose_name='Bio', blank=True, null=True)
    email = models.EmailField(unique=True, max_length=50,  blank=False, null=False)

    def get_absolute_url(self):
        return f'/{self.slug}/'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(User, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

class category(models.Model):

    cat = (
        ('blockchain', 'Blockchain'),
        ('equity', 'Equity'),
        ('economic', 'Economic'),
        ('geopolitics', 'Geopolitics')
    )

    cat_title = models.CharField(max_length=200, verbose_name='Category Title', choices=cat, default='---')
    slug =  models.SlugField(max_length=5500, verbose_name='Slug', unique=True)
    # description = models.TextField(max_length=500, verbose_name='Category Description')
    
    def __str__(self) -> str:
        return self.cat_title

class post(models.Model):

    categories = models.ForeignKey(
        category,
        on_delete=models.CASCADE,
        to_field='slug'
    )
    title = models.CharField(max_length=200, verbose_name='Title')
    slug =  models.SlugField(max_length=5500, verbose_name='Slug', unique=True)
    picked = models.BooleanField(verbose_name='Editors Pick')
    author = models.ForeignKey(User, on_delete=models.CASCADE, to_field='slug')
    publishedAt = models.DateTimeField(auto_now_add=True, verbose_name='Published At')
    summary = models.TextField(max_length=500, verbose_name='Summary')
    sub_topic = models.TextField(max_length=100, verbose_name='Sub Topic', blank=True, null=True)
    body = RichTextField()
    mainImage = models.ImageField(upload_to='post')
    video = models.FileField(upload_to='post/vd_uploads', blank=True, null=True)
    image_slide = models.ManyToManyField('imageShow')

    class Meta:
        ordering = ('-publishedAt',)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return f'/{self.categories.slug}/{self.slug}/'

    def __str__(self) -> str:
        return self.title

def update_filename(instance, filename):
        path = "post/sldh/"
        format = filename + instance.file_extension
        return os.path.join(path, format)

class imageShow(models.Model):
    posts = models.ForeignKey(post, on_delete=models.CASCADE, to_field='slug')
    image_slide = models.ImageField(upload_to=update_filename, null=True)

    def __str__(self) -> str:
        return str(self.image_slide)

class postReview(models.Model):

    state = (
        ('Rejected', 'Rejected'),
        ('InReview', 'In Review'),
        ('Approved', 'Approved'),
    )
    
    post = models.ForeignKey(post, on_delete=models.CASCADE, to_field='slug')
    review = models.CharField(max_length=200, verbose_name='Review', choices=state, default='InReview')

    def __str__(self) -> str:
        return f'({self.review}) {self.post}'

class subscribedUsers(models.Model):
    email = models.EmailField(unique=True, max_length=50)

    def __str__(self) -> str:
        return self.email

class comment(models.Model):
    post = models.ForeignKey(post, on_delete=models.CASCADE, to_field='slug')
    name = models.CharField(max_length=80)
    email = models.EmailField(blank=True, null=True)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    email_plaintext_message = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)

    send_mail(
        # title:
        "Password Reset for {title}".format(title="SMC Blog"),
        # message:
        email_plaintext_message,
        # from:
        "noreply@smcblog.com",
        # to:
        [reset_password_token.user.email]
    )
