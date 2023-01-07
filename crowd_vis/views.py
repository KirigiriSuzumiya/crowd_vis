import subprocess
from time import sleep
import os
import cv2
import json
import datetime
import threading
import time
import numpy as np
from pyecharts.charts import Line,Pie
from pyecharts import options as opts

from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from pyecharts.components import Table

from .settings import BASE_DIR
from django.shortcuts import render
from dbmodel.models import crowdinfo, warning


def pp_human_service(show_id):
    # PP-Human后台进程
    while True:
        pp_human_path = os.path.join(BASE_DIR, "pp-human", "pipeline", "pipeline.py ")
        yml_path = os.path.join(BASE_DIR, "pp-human", "pipeline", "config", "infer_cfg_pphuman.yml ")
        test_video_path = os.path.join(BASE_DIR, 'test'+str(show_id)+'.mp4')
        # shell = r'python ' + pp_human_path + '--config ' + yml_path + r' --camera_id=0 --device=gpu --output_dir=output --do_entrance_counting'
        shell = r'python ' + pp_human_path + '--config ' + yml_path + r' --video_file=' + test_video_path + \
                ' --run_mode=openvino --output_dir=output --do_entrance_counting --show_id=%d' % show_id
        # subprocess.run(shell, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        print(shell)
        subprocess.run(shell)


context = None


def info_update_service(num):
    # 数据采集入库后台进程
    global context
    for i in range(num):
        txt_path = os.path.join(BASE_DIR, 'records{}.txt'.format(i+1))
        while True:
            total, in_count, out_count, vis_count = 0, 0, 0, 0
            try:
                fp = open(txt_path, 'r')
                info = json.load(fp)
                fp.close()
                vis_count += info[1]
                info = info[0]
                info = info[info.find("Total count: ") + 13:]
                total += eval(info[:info.find(',')])
                info = info[info.find(":") + 2:]
                in_count += eval(info[:info.find(',')])
                info = info[info.find(":") + 2:]
                out_count += eval(info[:-1])
                count0, count1, count2, count3, count4 = total % 10, total // 10 % 10, total // 100 % 10, total // 1000 % 10, total // 10000 % 10
                context = [total, vis_count, in_count, out_count, count0, count1, count2, count3, count4]
                db_obj = crowdinfo(total_count=total, in_count=in_count,
                                   out_count=out_count,
                                   vis_count=vis_count)
                db_obj.save()
                sleep(2)
            except Exception as e:
                sleep(2)
                print("db saving failed!")
                print(e)
                pass

# 多镜子进程与数据进库子进程
t1 = threading.Thread(target=pp_human_service, args=(1,))
t1.setDaemon(True)
t1.start()
# t2 = threading.Thread(target=pp_human_service, args=(2,))
# t2.setDaemon(True)
# t2.start()
t0 = threading.Thread(target=info_update_service, args=(1,))
t0.setDaemon(True)
t0.start()


def video_display(show_id):
    # 流式视频传输迭代器
    txt_path = os.path.join(BASE_DIR, 'frame%d.txt' % show_id)
    while True:
        fp = open(txt_path, 'rb')
        info = fp.read()
        fp.close()
        if info:
            yield b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + info + b'\r\n'


def video(request, show_id):
    # 使用流传输传输视频流
    show_id = eval(show_id)
    return StreamingHttpResponse(video_display(show_id), content_type='multipart/x-mixed-replace; boundary=frame')


def num_count(request):
    # ajax动态更新人流量
    global context
    return JsonResponse(context, safe=False)


def index(request):
    # 主页views
    return render(request, "index.html")


def graph_vis(request):
    # 人流折线图,数据表格，饼图，警告列表数据更新
    x_data = []
    vis_data = []
    in_data = []
    out_data = []
    table_data = []
    pie_data = []
    warning_data = ''
    for warn in warning.objects.all().order_by('-warn_time')[:5]:
        warning_data += """
        <div class="message_scroll_box">
            <div class="message_scroll">
                <div class="scroll_top">
                    <span class="scroll_title">{}</span>
                    <span class="scroll_level scroll_level01">报警时间</span>
                    <span class="scroll_timer">{}</span>
                </div>
                <div class="msg_cage">
                    <a class="localize_title">报警监控：{}号</a>
                </div>
                <div class="msg_cage">
                    <a class="localize_msg">{}</a>
                </div>
            </div>
        </div>
        """.format(warn.warn_type, warn.warn_time.strftime("%m-%d %H:%M:%S"), warn.camera_id, warn.info)
    warning_data = warning_data.replace('\n', '').replace('"', "'")
    for info in crowdinfo.objects.all().order_by('-shoot_time')[:20]:
        if not pie_data:
            pie_data = [("滞留量", info.total_count-info.in_count-info.out_count),
                        ("流入量", info.in_count),
                        ("流出量", info.out_count)]
        x_data.append(info.shoot_time.strftime("%Y-%m-%d %H:%M:%S"))
        vis_data.append(info.vis_count)
        in_data.append(info.in_count)
        out_data.append(info.out_count)
        table_data.append([info.shoot_time.strftime("%y-%m-%d %H:%M:%S"), info.total_count, info.vis_count, info.out_count, info.in_count])
    data1 = (
        Line()
        .add_xaxis(x_data)
        .add_yaxis("进入人流", in_data, is_smooth=True, symbol_size=10, is_connect_nones=True, color='red',
                   linestyle_opts=opts.series_options.LineStyleOpts(width=3))
        .add_yaxis("出口人流", out_data, is_smooth=True, symbol_size=10, is_connect_nones=True, color='green',
                   linestyle_opts=opts.series_options.LineStyleOpts(width=3))
        .set_global_opts(legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')),
                         xaxis_opts=opts.AxisOpts(type_='time',
                                                  axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(
                                                      color='white'))),
                         yaxis_opts=opts.AxisOpts(axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(
                             color="white"))),
                         )
        .dump_options_with_quotes()
    )
    data2 = (
        Line()
        .add_xaxis(x_data)
        .add_yaxis("在镜人流", vis_data, is_smooth=True, symbol_size=10, is_connect_nones=True, color='red',
                   linestyle_opts=opts.series_options.LineStyleOpts(width=3))
        .set_global_opts(legend_opts=opts.LegendOpts(textstyle_opts=opts.TextStyleOpts(color='white')),
                         xaxis_opts=opts.AxisOpts(type_='time',
                                                  axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(
                                                                                            color='white'))),
                         yaxis_opts=opts.AxisOpts(axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(
                                                                                            color="white"))),
                         )
        .dump_options_with_quotes()
    )
    data3 = (
        Table()
        .add(headers=['采集时间', '总人流', '在镜人流', '出口人流', '进口人流'],
             rows=table_data)
        .render('statics/render.html')
    )
    data3 = open('statics/render.html', 'r', encoding='utf-8').read()
    data3 = data3[data3.find("<table"):data3.find("</table>")]
    data3 = data3.replace('\n', '').replace('"', "'")
    data4 = (
        Pie()
        .add('', pie_data, center=['50%', '60%'], radius='70%')
        .set_global_opts(title_opts=opts.TitleOpts(title="人流状态分布",
                                                   title_textstyle_opts=opts.TextStyleOpts(color="white")),
                         legend_opts=opts.LegendOpts(orient='vertical', pos_left='right',
                                                     textstyle_opts=opts.TextStyleOpts(color='white')))
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .set_colors(["red", "yellow",  "pink", "orange", "purple"])
        .dump_options_with_quotes()
    )
    data1 = json.loads(data1)
    data2 = json.loads(data2)
    data3 = json.dumps(data3, ensure_ascii=False)
    data3 = data3.replace('"', '')
    data4 = json.loads(data4)
    data5 = json.dumps(warning_data, ensure_ascii=False)
    data5 = data5.replace('"', '')
    data = {
        "code": 200,
        "msg": "success",
        "data": [data1, data2, data3, data4, data5]
    }
    return JsonResponse(data)


def test(request):
    return render(request, "camera.html")


def warning_url(request, warning_type):
    warn_obj = warning(warn_type=warning_type, camera_id=1, info="待处理")
    warn_obj.save()
    return HttpResponse(200)
    pass
