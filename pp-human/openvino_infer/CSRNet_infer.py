from openvino.inference_engine import IECore
import numpy as np
import os
import openvino.runtime as ov
import cv2


class CSRNet_predictor(object):
    def __init__(self, onnxfile, core):
        if not os.path.exists(onnxfile):
            onnxfile = os.path.join(os.path.dirname(onnxfile),"model.pdmodel")
        self.core = core
        self.compiled_model = self.core.compile_model(onnxfile, "AUTO")
        self.infer_request = self.compiled_model.create_infer_request()
        print("[OpenVINO]%s infer request created" % onnxfile)

    def run(self, inputs):
        # Create tensor from external memory
        inputs = inputs["image"]
        inputs = cv2.resize(inputs, (640, 480))
        inputs = inputs / 255.0
        inputs = inputs.T.reshape(3, 640, 480).astype('float32')
        inputs = np.array([inputs], "float32")
        input_tensor = ov.Tensor(array=inputs, shared_memory=True)
        # Set input tensor for model with one input
        self.infer_request.set_input_tensor(input_tensor)
        self.infer_request.start_async()
        self.infer_request.wait()
        # Get output tensor for model with one output
        output = self.infer_request.get_output_tensor(0)
        output_buffer = output.data
        temp = output_buffer[0][0]
        temp_sum = np.sum(temp) / 100
        if ((-np.floor(temp_sum) + temp_sum) > 0.5):
            people = np.ceil(temp_sum)
        else:
            people = np.floor(temp_sum)
        return people


# core = ov.Core()
# onnxfile = r"C:\Users\uif80295\Documents\GitHub\crowd_vis_openvino\pp-human\pipeline\model\onnx_CSRNet\model.onnx"
# test = CSRNet_predictor(onnxfile, core)
# import cv2
# inputs = {"image": cv2.imread("data/Picture1.jpg")}
# out = test.run(inputs)
# print("people {}".format(out))
