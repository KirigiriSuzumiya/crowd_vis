import numpy as np
import openvino.runtime as ov
# from openvino.inference_engine import IENetwork, IECore, ExecutableNetwork

class video_predictor(object):
    def __init__(self, onnxfile, core):
        self.core = core
        self.compiled_model = self.core.compile_model(onnxfile, "AUTO")
        self.infer_request = self.compiled_model.create_infer_request()
        print("[OpenVINO]%s infer request created" % onnxfile)

    def run(self, inputs):
        # print(inputs.shape)
        # Create tensor from external memory
        input_tensor = ov.Tensor(array=inputs[0][0], shared_memory=True)
        # Set input tensor for model with one input
        self.infer_request.set_input_tensor(input_tensor)
        self.infer_request.start_async()
        self.infer_request.wait()
        # Get output tensor for model with one output
        output = self.infer_request.get_output_tensor()
        output_buffer = output.data
        return output_buffer


# class old_video_predictor(object):
#     def __init__(self, onnxfile):
#         # 读取并解析模型
#         ie = IECore()
#         net = ie.read_network(onnxfile)
#         # 原模型为动态图，需要固定模型输入shape
#         net.reshape({'data_batch_0': (1, 8, 3, 320, 320)})
#         self.predictor = ie.load_network(net, 'CPU')
#
#
#     def run(self, inputs):
#         # output_buffer[] - accessing output tensor data
#         outputs = self.predictor.infer({'data_batch_0': inputs[0][0]})
#         return outputs['linear_2.tmp_1']


# core = ov.Core()
# onnxfile = r"C:\Users\SVAI-BOX-I78C\Desktop\project\crowd_vis\pp-human\pipeline\model\onnx_ppTSM\ppTSM.onnx"
# inputs = np.load("inputs.npy")
# test = video_predictor(onnxfile, core)
# output = test.run(inputs)
# print(output, type(output))
# test = old_video_predictor(onnxfile)
# output = test.run(inputs)
# print(output, type(output))


