from .models import warning, crowdinfo,statistic_crowdinfo
from django.http import JsonResponse
import datetime
from django.core.paginator import Paginator
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

def deal_crowdinfo(request):
    page=request.GET.get('page')

    start_y=request.GET.get('start_y')
    start_m=request.GET.get('start_m')
    start_d=request.GET.get('start_d')
    start_h=request.GET.get('start_h')

    end_y=request.GET.get('end_y')
    end_m=request.GET.get('end_m')
    end_d=request.GET.get('end_d')
    end_h=request.GET.get('end_h')

    start_time=datetime.datetime(int(start_y),int(start_m),int(start_d),int(start_h))
    end_time=datetime.datetime(int(end_y),int(end_m),int(end_d),int(end_h))


    res=statistic_crowdinfo.objects.filter(time_frame__range=[start_time,end_time]).all().values()
    page_num=len(res)
    if page_num % 10 != 0:
        page_num=page_num//10+1
    else:
        page_num=page_num//10

    per_page=10
    paginator = Paginator(res, per_page)
    n_res=paginator.get_page(page)
    n_res=list(n_res)


    data={"result": n_res,"page_num":page_num}
    return JsonResponse(data, json_dumps_params={"ensure_ascii": False},safe=False)
def deal_warning(request):
    pass



