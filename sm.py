import torch
state = torch.load("cataract_cnn_weighted.pth", map_location="cpu")
print(len(state))  # should list all layer weight keys
