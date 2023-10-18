import argparse
import os
import sys
import torch

# Workaround to resolve chaiNNer module deps
current_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_directory, "chaiNNer/backend/src"))

from chaiNNer.backend.src.packages.chaiNNer_pytorch.pytorch.io.load_model import load_model_node

if __name__ == '__main__':
    """Convert pytorch model to onnx models"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, help='Input model path', required=True)
    parser.add_argument('--output', type=str, help='Output onnx path', required=True)

    args = parser.parse_args()
    
    (model, _, _) = load_model_node(args.input)
    # set the train mode to false since we will only run the forward pass.
    model.train(False)
    model.cpu().eval()

    # An example input
    x = torch.rand(1, model.in_nc, 256, 256)
    # Export the model
    with torch.no_grad():
        dynamic_axes = {'input':{0:'batch_size' , 2:'width', 3:'height'}, 'output':{0:'batch_size' , 2:'width', 3:'height'}}
        torch.onnx.export(
            model,
            x,
            args.output,
            opset_version=11,
            export_params=True,
            input_names = ['input'],
            output_names = ['output'], 
            dynamic_axes=dynamic_axes)
