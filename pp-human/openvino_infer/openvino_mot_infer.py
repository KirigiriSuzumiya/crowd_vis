import os
import datetime
import sys

import yaml
import numpy as np
from openvino.inference_engine import IENetwork, IECore, ExecutableNetwork
import openvino.runtime as ov


# add deploy path of PadleDetection to sys.path
parent_path = os.path.dirname(os.path.dirname(os.path.join(__file__)))
sys.path.insert(0, parent_path)
from pptracking.python.mot.tracker import OCSORTTracker
from openvino_infer.openVinopreprocess import Compose


# Global dictionary
SUPPORT_MODELS = {
    'YOLO', 'RCNN', 'SSD', 'Face', 'FCOS', 'SOLOv2', 'TTFNet', 'S2ANet', 'JDE',
    'FairMOT', 'DeepSORT', 'GFL', 'PicoDet', 'CenterNet', 'TOOD', 'RetinaNet',
    'StrongBaseline', 'STGCN', 'YOLOX', 'HRNet'
}


class PredictConfig(object):
    """set config of preprocess, postprocess and visualize
    Args:
        infer_config (str): path of infer_cfg.yml
    """

    def __init__(self, infer_config):
        # parsing Yaml config for Preprocess
        with open(infer_config) as f:
            yml_conf = yaml.safe_load(f)
        self.check_model(yml_conf)
        self.arch = yml_conf['arch']
        self.preprocess_infos = yml_conf['Preprocess']
        self.min_subgraph_size = yml_conf['min_subgraph_size']
        self.label_list = yml_conf['label_list']
        self.use_dynamic_shape = yml_conf['use_dynamic_shape']
        self.draw_threshold = yml_conf.get("draw_threshold", 0.5)
        self.mask = yml_conf.get("mask", False)
        self.tracker = yml_conf.get("tracker", None)
        self.nms = yml_conf.get("NMS", None)
        self.fpn_stride = yml_conf.get("fpn_stride", None)
        if self.arch == 'RCNN' and yml_conf.get('export_onnx', False):
            print(
                'The RCNN export model is used for ONNX and it only supports batch_size = 1'
            )
        self.print_config()

    def check_model(self, yml_conf):
        """
        Raises:
            ValueError: loaded model not in supported model type
        """
        for support_model in SUPPORT_MODELS:
            if support_model in yml_conf['arch']:
                return True
        raise ValueError("Unsupported arch: {}, expect {}".format(yml_conf[
            'arch'], SUPPORT_MODELS))

    def print_config(self):
        print('-----------  Model Configuration -----------')
        print('%s: %s' % ('Model Arch', self.arch))
        print('%s: ' % ('Transform Order'))
        for op_info in self.preprocess_infos:
            print('--%s: %s' % ('transform op', op_info['type']))
        print('--------------------------------------------')

class label(object):
    def __init__(self):
        self.labels = ['pedestrian']

class OpenvineDetector(object):

    def __init__(self, onnxfile, infer_cfg, core):
        self.onnx_file = onnxfile
        self.infer_cfg = infer_cfg
        self.infer_config = PredictConfig(infer_cfg)
        self.pred_config = label()
        det_thresh = 0.4
        max_age = 30
        min_hits = 3
        iou_threshold = 0.3
        delta_t = 3
        inertia = 0.2
        min_box_area = 0
        vertical_ratio = 0
        use_byte = False

        self.tracker = OCSORTTracker(
            det_thresh=det_thresh,
            max_age=max_age,
            min_hits=min_hits,
            iou_threshold=iou_threshold,
            delta_t=delta_t,
            inertia=inertia,
            min_box_area=min_box_area,
            vertical_ratio=vertical_ratio,
            use_byte=use_byte)
        self.core = core
        self.model = self.core.read_model(onnxfile)
        if "onnx_picodet" in onnxfile:
            self.model.reshape({0: [1, 3, 320, 320], 1: [1, 2]})
        else:
            self.model.reshape({0: [1, 3, 640, 640], 1: [1, 2]})
        self.compiled_model = self.core.compile_model(self.model, "GPU")
        self.predictor = self.compiled_model.create_infer_request()
        print("[OpenVINO]%s infer request created" % onnxfile)
        # # 初始化Inference Engine对象
        # ie = IECore()
        #
        # # 读取并解析模型
        # net = ie.read_network(onnxfile)
        # # 原模型为动态图，需要固定模型输入shape
        # if "onnx_picodet" in onnxfile:
        #     net.reshape({'image': (3, 320, 320), 'scale_factor': (1, 2)})
        # else:
        #     net.reshape({'image': (3, 640, 640), 'scale_factor': (1, 2)})
        #
        # self.predictor = ie.load_network(net, 'GPU')
        # assert isinstance(self.predictor, ExecutableNetwork)

    def det_predict(self, img_list):
        result = []
        # load preprocess transforms
        transforms = Compose(self.infer_config.preprocess_infos)
        # predict image
        for img_path in img_list:
            inputs = transforms(img_path)
            # Create tensor from external memory
            np_image = np.array([inputs['image']], dtype="float32")
            np_scale_factor = np.array([inputs['scale_factor']])
            image_tensor = ov.Tensor(array=np_image, shared_memory=True)
            scale_factor_tensor = ov.Tensor(array=np_scale_factor, shared_memory=True)
            # Set input tensor for model with one input
            self.predictor.set_input_tensor(0, image_tensor)
            self.predictor.set_input_tensor(1, scale_factor_tensor)
            self.predictor.start_async()
            self.predictor.wait()
            # Get output tensor for model with one output
            output_0 = self.predictor.get_output_tensor(0)
            output_1 = self.predictor.get_output_tensor(1)
            outputs = [output_0.data, output_1.data]
            # outputs = self.predictor.infer({'image': inputs['image'], 'scale_factor': inputs['scale_factor']})
            # print("Openvino predict: ")
            if self.infer_config.arch in ["HRNet"]:
                print(np.array(outputs[0]))
            else:
                # bboxes = np.array(outputs["multiclass_nms3_0.tmp_0"])
                bboxes = np.array(outputs[0])
                return bboxes

    def track(self, det_result):
        pred_embs = None
        pred_dets = det_result
        online_targets = self.tracker.update(pred_dets, pred_embs)
        online_tlwhs = list()
        online_scores = list()
        online_ids = list()
        for t in online_targets:
            tlwh = [t[0], t[1], t[2] - t[0], t[3] - t[1]]
            tscore = float(t[4])
            tid = int(t[5])
            if tlwh[2] * tlwh[3] <= self.tracker.min_box_area: continue
            if self.tracker.vertical_ratio > 0 and tlwh[2] / tlwh[
                3] > self.tracker.vertical_ratio:
                continue
            if tlwh[2] * tlwh[3] > 0:
                online_tlwhs.append(tlwh)
                online_ids.append(tid)
                online_scores.append(tscore)
        tracking_outs = {
            'online_tlwhs': online_tlwhs,
            'online_scores': online_scores,
            'online_ids': online_ids,
        }
        return tracking_outs

    def predict_image(self, im, visual=False):
        # np.save("mot_input.npy", im)
        bboxes = self.det_predict([im])
        tracking_outs = self.track(bboxes)
        online_tlwhs = [tracking_outs['online_tlwhs']]
        online_scores = [tracking_outs['online_scores']]
        online_ids = [tracking_outs['online_ids']]
        return [[online_tlwhs, online_scores, online_ids]]


# core = ov.Core()
# detector = OpenvineDetector(r"C:\Users\SVAI-BOX-I78C\Desktop\project\crowd_vis\pp-human\pipeline\model\onnx_human_s\model.onnx",
#                             r"C:\Users\SVAI-BOX-I78C\Desktop\project\crowd_vis\pp-human\pipeline\model\onnx_human_s\infer_cfg.yml",
#                             core)
# result = detector.predict_image(np.load(r"C:\Users\SVAI-BOX-I78C\Desktop\project\crowd_vis\pp-human\openvino_infer\mot_input.npy"))
# print(result)

# [[[[[719.9345722701155, 630.442996042123, 260.69500340898776, 449.855218853254], [1520.1372046204265, 374.152763879438, 257.46399407945955, 706.6260518309678]]], [[0.660973310470581, 0.9182507395744324]], [[2, 1]]]]




