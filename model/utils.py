from PIL import Image
from model.detector import detect_faces
from model.align_trans import get_reference_facial_points, warp_and_crop_face
import numpy as np
from model import extract_feature_v2
from model import model_irse
import torch
import io
import boto3




MODEL_ROOT = './model/pretrained_models/pretrained.pth'

crop_size = 128  # specify size of aligned faces, align and crop with padding
scale = crop_size / 112.
reference = get_reference_facial_points(default_square=True) * scale
backbone = model_irse.IR_50([112, 112])
backbone.load_state_dict(torch.load(MODEL_ROOT, map_location='cpu'))


def get_feature(pil_img):
    _, landmarks = detect_faces(pil_img)

    # if no face detected on picture
    if isinstance(landmarks, list):
        return -1
    elif landmarks.shape[0] > 1:
        return -2

    facial5points = [[landmarks[0][j], landmarks[0][j + 5]] for j in range(5)]

    warped_face = warp_and_crop_face(np.array(pil_img), facial5points, reference, crop_size=(crop_size, crop_size))
    img_warped = Image.fromarray(warped_face)
    features = extract_feature_v2.extract_feature(img_warped, backbone=backbone)
    return features


