import os
import sys

# Workaround to resolve chaiNNer module deps
current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(current_directory, "chaiNNer/backend/src"))
