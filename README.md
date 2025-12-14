# CatScan  
**An AI-Powered Mobile Application for Early Cataract Detection in Rural India**

## Overview
CatScan is a low-cost, AI-enabled mobile application designed to support early cataract screening in rural and underserved communities. The app enables volunteers to capture eye images using a smartphone and obtain fast, offline predictions using a lightweight convolutional neural network (CNN).

The project was developed in collaboration with ophthalmologists from the **Lokeswarananda Eye Foundation**, with a strong focus on accessibility, reliability, and real-world deployment constraints.

---

## Motivation
In many rural regions, access to ophthalmic care is limited by distance, cost, and availability of trained professionals. As a result, cataracts are often detected late, increasing the risk of preventable blindness.

CatScan aims to:
- Enable early screening without hospital visits  
- Reduce travel and financial burden on patients  
- Support volunteer-led triage in low-resource environments  

---

## Key Features
- Offline, on-device AI inference  
- Lightweight CNN optimized using TorchScript  
- Guided eye image capture and pupil-centric cropping  
- Local patient visit database with history tracking  
- Volunteer-friendly workflow and interface  
- Designed for low-connectivity rural settings  

---

## System Overview
The CatScan pipeline consists of:
1. Eye image capture via smartphone camera  
2. Pupil-centric preprocessing and cropping  
3. On-device CNN inference  
4. Prediction storage and visit logging  
5. Optional review and follow-up by ophthalmologists  

The system prioritizes bias reduction, speed, and robustness under varied lighting and device conditions.

---

## Model Summary
- Architecture: Lightweight CNN (CataractCNN)  
- Input size: 128 × 128 RGB images  
- Inference: Fully offline using TorchScript  

**Performance**
- Training accuracy: 96%  
- Validation accuracy: 93%  
- F1-score: 0.92  
- Inference time: < 1 second on mid-range Android devices  
