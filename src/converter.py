import argparse
import torch

from chaiNNer.backend.src.packages.chaiNNer_pytorch.pytorch.io.load_model import load_model_node

def convert_pth_to_onnx(input_model: str, output_model: str):
    (model, _, _) = load_model_node(input_model)
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
            output_model,
            opset_version=11,
            export_params=True,
            input_names = ['input'],
            output_names = ['output'], 
            dynamic_axes=dynamic_axes)

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
