import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import torch.nn.functional as F

# ----------------------------
# 1. Data Preparation
# ----------------------------
data_dir = "saved_images"

transform = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

dataset = datasets.ImageFolder(root=data_dir, transform=transform)

# ns1 -> Cataract (0), no_cataract -> Non-Cataract (1)
dataset.class_to_idx = {'ns1': 0, 'no_cataract': 1}
print("Classes:", dataset.classes)
print("Mapping:", dataset.class_to_idx)

train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

# ----------------------------
# 2. Model Definition
# ----------------------------
class CataractCNN(nn.Module):
    def __init__(self):
        super(CataractCNN, self).__init__()
        self.conv_layers = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
        )
        self.fc_layers = nn.Sequential(
            nn.Linear(64 * 16 * 16, 128),
            nn.ReLU(),
            nn.Linear(128, 2)
        )

    def forward(self, x):
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)
        x = self.fc_layers(x)
        return x


model = CataractCNN()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# ----------------------------
# Helper: Compute blue similarity (0–1)
# ----------------------------
def compute_blue_score(img_tensor):
    """
    img_tensor: normalized RGB tensor [3,H,W]
    Returns: scalar (0–1) indicating closeness to blue
    """
    img = img_tensor.clone().detach().cpu()
    img = img * torch.tensor([0.229, 0.224, 0.225]).view(3,1,1) + torch.tensor([0.485, 0.456, 0.406]).view(3,1,1)
    img = torch.clamp(img, 0, 1)

    R = img[0].mean().item()
    G = img[1].mean().item()
    B = img[2].mean().item()

    # Distance to blue (0,0,1)
    dist = ((R - 0)**2 + (G - 0)**2 + (B - 1)**2) ** 0.5
    blue_score = 1 - min(dist, 1.0)  # closer to 1 = more blue
    return blue_score

# ----------------------------
# 3. Training Loop
# ----------------------------
epochs = 10
for epoch in range(epochs):
    # --- Training ---
    model.train()
    running_loss, correct, total = 0.0, 0, 0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    train_acc = 100 * correct / total

    # --- Validation (with 80% blue weighting) ---
    model.eval()
    val_correct, val_total = 0, 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            probs = F.softmax(outputs, dim=1)  # CNN probabilities

            # Blend model output (20%) + blue score (80%)
            final_preds = []
            for i in range(images.size(0)):
                blue_score = compute_blue_score(images[i])
                cataract_prob = 0.5 * blue_score + 0.5 * probs[i, 0].item()  # class 0 = cataract
                pred_label = 0 if cataract_prob >= 0.5 else 1
                final_preds.append(pred_label)

            final_preds = torch.tensor(final_preds).to(device)
            val_total += labels.size(0)
            val_correct += (final_preds == labels).sum().item()

    val_acc = 100 * val_correct / val_total
    print(f"Epoch {epoch+1}/{epochs}, "
          f"Loss: {running_loss:.3f}, "
          f"Train Acc: {train_acc:.2f}%, "
          f"Val Acc: {val_acc:.2f}%")

# ----------------------------
# 4. Save Model
# ----------------------------
torch.save(model.state_dict(), "cataract_cnn_weighted.pth")
print("Model saved as cataract_cnn_weighted.pth")
