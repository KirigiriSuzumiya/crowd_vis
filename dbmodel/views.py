from .models import warning, crowdinfo
from django.http import JsonResponse


def my_view(request):
    res = warning.objects.all().values()
    res = list(res)
    data = {"result": res}
    return JsonResponse(data, json_dumps_params={"ensure_ascii": False})


def my_info(request):
    res = crowdinfo.objects.all().values()
    res = list(res)
    data = {"result": res}
    return JsonResponse(data, json_dumps_params={"ensure_ascii": False})


def deal_warning(request):
    pass