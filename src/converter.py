import torch
from spandrel.architectures.DAT import DAT
from spandrel.architectures.GFPGAN import GFPGAN
from spandrel.architectures.RestoreFormer import RestoreFormer

from spandrel import ModelLoader

class BlacklistedModelArchError(Exception):
    pass

def convert_pth_to_onnx(input_model: str, output_model: str):
    model_descriptor = ModelLoader().load_from_file(input_model)
    
    if model_descriptor.model.__class__.__name__ in (DAT.__name__, GFPGAN.__name__, RestoreFormer.__name__):
        raise BlacklistedModelArchError()

    # set the train mode to false since we will only run the forward pass.
    model_descriptor.train(False)
    model_descriptor.cpu().eval()

    # An example input
    x = torch.rand(1, model_descriptor.input_channels, 256, 256)
    # Export the model
    with torch.no_grad():
        dynamic_axes = {'input':{0:'batch_size', 2:'width', 3:'height'}, 'output':{0:'batch_size', 2:'width', 3:'height'}}
        torch.onnx.export(
            model_descriptor.model,
            x,
            output_model,
            opset_version=17,
            export_params=True,
            input_names = ['input'],
            output_names = ['output'], 
            dynamic_axes=dynamic_axes)
