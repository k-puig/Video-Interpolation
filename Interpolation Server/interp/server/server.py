import interp.nn.model as model

import torch
import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import StreamingResponse
from pathlib import Path

class InterpolationServerView:
    def __init__(self, output_dir:str, nn_params_file:str):
        self.router = APIRouter()
        self.router.add_api_route("/test", self.test_removethismethod, methods=["GET"])
        self.router.add_api_route("/upload", self.upload_video, methods=["POST"])
        self.router.add_api_route("/exists/{filename}", self.check_file_exists, methods=["GET"])
        self.router.add_api_route("/{filename}", self.get_video, methods=["GET"])
        
        self.output_dir.mkdir(exist_ok=True)
        self.output_dir = output_dir
        self.model = model.Interpolator()
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(device)
        self.model.load_state_dict(torch.load(nn_params_file, weights_only=True))
        self.model.eval()
        pass
    
    async def upload_video(self, file: UploadFile = File(...)):
        # Generate a future filename
        future_filename = file.filename
        file_path = self.output_dir / future_filename

        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        return {"filename": future_filename}
    
    async def check_file_exists(self, filename: str):
        file_path = self.output_dir / filename
        if file_path.exists():
            return {"exists": True}
        return {"exists": False}
    
    async def get_video(self, filename: str):
        file_path = self.output_dir / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return StreamingResponse(open(file_path, "rb"), media_type="video/mp4")
    
    
    def test_removethismethod() -> dict:
        return {"message": "Hello world"}
    
    def interpolate_and_save(self, input_video:str, output_video:str):
        pass
    
    # Saves to a new file in output_dir
    def _save_data(self, data:bytes, filename:str):
        file_path = self.output_dir / filename
        with open(file_path, "wb") as f:
            f.write(data)
        pass