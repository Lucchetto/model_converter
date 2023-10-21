import argparse

from .converter import convert_pth_to_onnx

if __name__ == '__main__':
    """Convert pytorch model to onnx models"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, help='Input model path', required=True)
    parser.add_argument('--output', type=str, help='Output onnx path', required=True)

    args = parser.parse_args()

    convert_pth_to_onnx(args.input, args.output)
