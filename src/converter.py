import torch
from chaiNNer.backend.src.nodes.impl.pytorch.architecture.DAT import DAT
from chaiNNer.backend.src.nodes.impl.pytorch.architecture.face.codeformer import CodeFormer
from chaiNNer.backend.src.nodes.impl.pytorch.architecture.face.gfpganv1_clean_arch import GFPGANv1Clean
from chaiNNer.backend.src.nodes.impl.pytorch.architecture.face.restoreformer_arch import RestoreFormer

from chaiNNer.backend.src.packages.chaiNNer_pytorch.pytorch.io.load_model import load_model_node

class UnsupportedModelArch(Exception):
    pass

def convert_pth_to_onnx(input_model: str, output_model: str):
    (model, _, _) = load_model_node(input_model)
    if model.__class__.__name__ in (DAT.__name__, CodeFormer.__name__, GFPGANv1Clean.__name__, RestoreFormer.__name__):
        raise UnsupportedModelArch()
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
