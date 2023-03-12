import os.path

import openvino.runtime as ov


class openvino_predictor(object):
    def __init__(self, onnxfile, core):
        if not os.path.exists(onnxfile):
            onnxfile = os.path.join(os.path.dirname(onnxfile),"model.pdmodel")
        self.core = core
        self.compiled_model = self.core.compile_model(onnxfile, "AUTO")
        self.infer_request = self.compiled_model.create_infer_request()
        print("[OpenVINO]%s infer request created" % onnxfile)

    def call_back(self, infer_request):
        output = self.infer_request.get_output_tensor(0)
        output_buffer = output.data
        print(output_buffer)
        return {'output': output_buffer}

    def run_async(self, inputs):
        inputs_temp = inputs["image"]
        input_tensor = ov.Tensor(array=inputs_temp, shared_memory=True)
        # Set input tensor for model with one input
        self.infer_request.set_input_tensor(input_tensor)
        self.infer_request.set_callback(self.call_back, "id")
        self.infer_request.start_async()

    def run(self, inputs):
        # Create tensor from external memory
        inputs_temp = inputs["image"]
        input_tensor = ov.Tensor(array=inputs_temp, shared_memory=True)
        # Set input tensor for model with one input
        self.infer_request.set_input_tensor(1,input_tensor)
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