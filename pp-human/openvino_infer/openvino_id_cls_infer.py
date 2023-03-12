import openvino.runtime as ov
import os


class id_cls_predictor(object):
    def __init__(self, onnxfile, core):
        if not os.path.exists(onnxfile):
            onnxfile = os.path.join(os.path.dirname(onnxfile),"model.pdmodel")
            # self.yoloe = True
        self.core = core
        self.compiled_model = self.core.compile_model(onnxfile, "AUTO")
        self.infer_request = self.compiled_model.create_infer_request()
        print("[OpenVINO]%s infer request created" % onnxfile)

    def run_yoloe(self, inputs):
        # Create tensor from external memory
        inputs_temp = inputs["image"]
        input_tensor = ov.Tensor(array=inputs_temp, shared_memory=True)
        # Set input tensor for model with one input
        self.infer_request.set_input_tensor(1, input_tensor)
        inputs_temp = inputs['scale_factor']
        input_tensor = ov.Tensor(array=inputs_temp, shared_memory=True)
        # Set input tensor for model with one input
        self.infer_request.set_input_tensor(0, input_tensor)
        self.infer_request.start_async()
        self.infer_request.wait()
        # Get output tensor for model with one output
        output_0 = self.infer_request.get_output_tensor(0)
        output_1 = self.infer_request.get_output_tensor(1)
        return dict(boxes=output_0.data, boxes_num=output_1.data)

    def run(self, inputs):
        try:
            # Create tensor from external memory
            inputs_temp = inputs["image"]
            input_tensor = ov.Tensor(array=inputs_temp, shared_memory=True)
            # Set input tensor for model with one input
            self.infer_request.set_input_tensor(1, input_tensor)
            inputs_temp = inputs['scale_factor']
            input_tensor = ov.Tensor(array=inputs_temp, shared_memory=True)
            # Set input tensor for model with one input
            self.infer_request.set_input_tensor(0, input_tensor)
            self.infer_request.start_async()
            self.infer_request.wait()
            # Get output tensor for model with one output
            output_0 = self.infer_request.get_output_tensor(0)
            output_1 = self.infer_request.get_output_tensor(1)
            return dict(boxes=output_0.data, boxes_num=output_1.data)
        except:
            # Create tensor from external memory
            inputs = inputs["image"]
            input_tensor = ov.Tensor(array=inputs, shared_memory=True)
            # Set input tensor for model with one input
            self.infer_request.set_input_tensor(input_tensor)
            self.infer_request.start_async()
            self.infer_request.wait()
            # Get output tensor for model with one output
            output = self.infer_request.get_output_tensor(0)
            output_buffer = output.data
            return {'output': output_buffer}


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
