from django.urls import path, include

# from django.contrib import admin

# admin.autodiscover()

import hello.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", hello.views.index, name="index"),
    path("api/currently_playing", hello.views.currently_playing, name="currently_playing"),
    path("api/get_history", hello.views.get_history, name="get_history"),
    path("api/send_song", hello.views.send_song, name="send_song"),
]
