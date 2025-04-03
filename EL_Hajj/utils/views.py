from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from .pass_gen import gen_pass_file


@api_view(["GET"])
@renderer_classes([JSONRenderer])
def gen_passwords(request):
    gen_pass_file()
    return Response({ "message": "generated passwords successfully" })
