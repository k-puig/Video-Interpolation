import interp.nn.model as model

import torch

from fastapi import FastAPI
from fastapi.routing import APIRouter

class InterpolationServerView:
    def __init__(self, output_dir:str, nn_params_file:str):
        self.router = APIRouter()
        self.router.add_api_route("/test", self.test_removethismethod, methods=["GET"])
        
        self.output_dir = output_dir
        self.model = model.Interpolator()
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(device)
        self.model.load_state_dict(torch.load(nn_params_file, weights_only=True))
        self.model.eval()
        pass
    
    def test_removethismethod() -> dict:
        return {"message": "Hello world"}
    
    def interpolate_and_save(self, input_video:str, output_video:str):
        pass
    
    # Saves to a new file in output_dir
    def _save_data(self, data:bytes, filename:str):
        pass