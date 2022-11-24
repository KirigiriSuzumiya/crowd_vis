from openvino.inference_engine import IECore
import numpy as np
import yaml
import os
import sys
from openVinopreprocess import Compose
import cv2
parent_path = os.path.abspath(os.path.join(__file__,))
sys.path.insert(0, parent_path)



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


class video_predictor(object):
    def __init__(self,onnxfile, infer_cfg):
        # 读取并解析模型
        ie = IECore()
        net = ie.read_network(onnxfile)
        # 原模型为动态图，需要固定模型输入shape
        net.reshape({'image': (1, 3, 320, 320)})
        self.predictor = ie.load_network(net, 'CPU')
        self.infer_config = PredictConfig(infer_cfg)

    def run(self, inputs):
        transforms = Compose(self.infer_config.preprocess_infos)
        inputs = transforms(inputs)
        print(inputs['image'].shape)
        outputs = self.predictor.infer({'image': inputs['image'], 'scale_factor': inputs['scale_factor']})
        return outputs


onnxfile = r"C:\Users\SVAI-BOX-I78C\Desktop\project\crowd_vis\pp-human\pipeline\model\onnx_picodet_human\model.onnx"
infer_cfg = r"C:\Users\SVAI-BOX-I78C\Desktop\project\crowd_vis\pp-human\pipeline\model\onnx_picodet_human\infer_cfg.yml"
inputs = cv2.imread(r"C:\Users\SVAI-BOX-I78C\Desktop\project\13.jpg")
inputs = cv2.cvtColor(inputs, cv2.COLOR_BGR2RGB)
test = video_predictor(onnxfile, infer_cfg)
output = test.run([inputs])
print(output, type(output))
