#%%
import torch
from torch.utils.data import Dataset, DataLoader
import json
from torchvision.transforms import Compose, Lambda
from torchvision.transforms._transforms_video import (
    CenterCropVideo,
    NormalizeVideo,
)
from pytorchvideo.data.encoded_video import EncodedVideo
from pytorchvideo.transforms import (
    ApplyTransformToKey,
    ShortSideScale,
    UniformTemporalSubsample,
    UniformCropVideo
)
from typing import Dict
import pandas as pd

# Device on which to run the model
# Set to cuda to load on GPU
device = "cpu"

# Pick a pretrained model and load the pretrained weights
model_name = "slowfast_r50"
model = torch.hub.load("facebookresearch/pytorchvideo", model=model_name, pretrained=True)

# Set to eval mode and move to desired device
model = model.to(device)
model = model.eval()

print("Model is loaded")
print(model)
print()
print("Model attributes: ", dir(model))
#print("Model parameters: ", model.parameters)
print("Model Final Block: ", model.blocks[6])
print("Model Final Block attributes: ", dir(model.blocks[6]))
print("Model Final Block proj: ", model.blocks[6].proj)



#FOUBD HOW TO CHOP OFF THIS FINAL LAYER
head_block = model.blocks[6]

# Check the input features to the proj layer, which we need to preserve
in_features = head_block.proj.in_features

# Replace the proj layer with a new one that outputs a single value
head_block.proj = torch.nn.Linear(in_features, 1)

print("New model head: ", model.blocks[6].proj)





video_csv = pd.read_csv("video_data.csv")

X_col = 'filename'
y_col = 'diggCount'

video_paths = video_csv[X_col]
target = video_csv[y_col]




# ####This is where the dataset is loaded
# #!wget https://dl.fbaipublicfiles.com/pyslowfast/dataset/class_names/kinetics_classnames.json


# with open("kinetics_classnames.json", "r") as f:
#     kinetics_classnames = json.load(f)

# # Create an id to label name mapping
# kinetics_id_to_classname = {}
# for k, v in kinetics_classnames.items():
#     kinetics_id_to_classname[v] = str(k).replace('"', "")
    
    
    
    
    
    
# ####################
# # SlowFast transform
# ####################

side_size = 256
mean = [0.45, 0.45, 0.45]
std = [0.225, 0.225, 0.225]
crop_size = 256
num_frames = 32
sampling_rate = 2
frames_per_second = 30
alpha = 4

class PackPathway(torch.nn.Module):
    """
    Transform for converting video frames as a list of tensors.
    """
    def __init__(self):
        super().__init__()

    def forward(self, frames: torch.Tensor):
        fast_pathway = frames
        # Perform temporal sampling from the fast pathway.
        slow_pathway = torch.index_select(
            frames,
            1,
            torch.linspace(
                0, frames.shape[1] - 1, frames.shape[1] // alpha
            ).long(),
        )
        frame_list = [slow_pathway, fast_pathway]
        return frame_list

transform =  ApplyTransformToKey(
    key="video",
    transform=Compose(
        [
            UniformTemporalSubsample(num_frames),
            Lambda(lambda x: x/255.0),
            NormalizeVideo(mean, std),
            ShortSideScale(
                size=side_size
            ),
            CenterCropVideo(crop_size),
            PackPathway()
        ]
    ),
)

# # The duration of the input clip is also specific to the model.
clip_duration = (num_frames * sampling_rate)/frames_per_second








####This is where an example video is loaded
#!wget https://dl.fbaipublicfiles.com/pytorchvideo/projects/archery.mp4


# Load the example video
video_path = "archery.mp4"

# Select the duration of the clip to load by specifying the start and end duration
# The start_sec should correspond to where the action occurs in the video
start_sec = 0
end_sec = start_sec + clip_duration

# Initialize an EncodedVideo helper class
video = EncodedVideo.from_path(video_path)

# Load the desired clip
video_data = video.get_clip(start_sec=start_sec, end_sec=end_sec)

# Apply a transform to normalize the video input
video_data = transform(video_data)

# Move the inputs to the desired device
inputs = video_data["video"]
inputs = [i.to(device)[None, ...] for i in inputs]







# Pass the input clip through the model
preds = model(inputs)




# Get the predicted classes
post_act = torch.nn.Softmax(dim=1)
preds = post_act(preds)
pred_classes = preds.topk(k=5).indices

# Map the predicted classes to the label names
pred_class_names = [kinetics_id_to_classname[int(i)] for i in pred_classes[0]]
print("Predicted labels: %s" % ", ".join(pred_class_names))