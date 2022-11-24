from openvino.inference_engine import IECore
import numpy as np
import pickle
import openvino.runtime as ov


class id_cls_predictor(object):
    def __init__(self, onnxfile, core):
        self.core = core
        self.compiled_model = self.core.compile_model(onnxfile, "AUTO")
        self.infer_request = self.compiled_model.create_infer_request()
        print("[OpenVINO]%s infer request created" % onnxfile)
        # # 读取并解析模型
        # ie = IECore()
        # net = ie.read_network(onnxfile)
        # # 原模型为动态图，需要固定模型输入shape
        # net.reshape({'x': (1, 3, 224, 224)})
        # self.predictor = ie.load_network(net, 'CPU')

    def run(self, inputs):
        # Create tensor from external memory
        inputs = inputs["image"]
        input_tensor = ov.Tensor(array=inputs, shared_memory=True)
        # Set input tensor for model with one input
        self.infer_request.set_input_tensor(input_tensor)
        self.infer_request.start_async()
        self.infer_request.wait()
        # Get output tensor for model with one output
        output = self.infer_request.get_output_tensor()
        output_buffer = output.data
        return {'output': output_buffer}
        # outputs = []
        # for im in inputs["image"]:
        #     output = self.predictor.infer({'x': im})
        #     outputs.append(output['softmax_1.tmp_0'][0])
        # outputs = np.array(outputs)
        # return {'output': outputs}


    def predict(self, inputs):
        # Create tensor from external memory
        inputs = inputs["image"]
        input_tensor = ov.Tensor(array=inputs, shared_memory=True)
        # Set input tensor for model with one input
        self.infer_request.set_input_tensor(input_tensor)
        self.infer_request.start_async()
        self.infer_request.wait()
        # Get output tensor for model with one output
        output = self.infer_request.get_output_tensor()
        output_buffer = output.data
        return {'output': output_buffer}

# core = ov.Core()
# onnxfile = r"C:\Users\SVAI-BOX-I78C\Desktop\project\crowd_vis\pp-human\pipeline\model\onnx_PPHGNet_calling\model.onnx"
# inputs = pickle.load(open("a.pkl", 'rb'))
# print(inputs["image"].shape)
# test = id_cls_predictor(onnxfile, core)
# output = test.run(inputs)
# print(output, type(output))

# [[0.11808661 0.88191336]
#  [0.09139209 0.9086079 ]
#  [0.04910688 0.9508931 ]
#  [0.0724176  0.9275824 ]
#  [0.23694623 0.7630538 ]
#  [0.12993938 0.8700607 ]
#  [0.13012154 0.8698785 ]
#  [0.04909197 0.950908  ]] <class 'numpy.ndarray'>
