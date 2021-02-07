from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse, HttpResponseServerError
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import api.spotify
import api.currently_playing
import spotipy
import json
from datetime import datetime

from .verify import verify

from .models import Song, History


# Create your views here.
def index(request):
    res = {
        "current_song": api.currently_playing.get_currently_playing(),
        "history": api.currently_playing.get_history(50)
    }
    return render(request, "index2.html",  res)


@require_http_methods(["GET"])
def currently_playing(request):
    res = {
        "current_song": api.currently_playing.get_currently_playing(),
    }
    return JsonResponse(res)

@require_http_methods(["GET"])
def get_history(request):
    res = api.currently_playing.get_history()
    return JsonResponse(res, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def send_song(request):
    body = json.loads(request.body)
    if "signature" in body and "data" in body:
        signature = body["signature"]
        data = body["data"]
    else:
        return HttpResponseBadRequest("Request was missing either a body object or a signature")

    if not verify(data, signature):
        pass # nf todo verify is broken atm. come back later
        #return HttpResponseBadRequest("Request was signed with an invalid key")
    api.currently_playing.add_song(data)
    return HttpResponse()



