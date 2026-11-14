import torch
import numpy as np

from PIL import Image
from transformers import CLIPProcessor, CLIPModel

from config import MODEL_NAME


class ImageEngine:

    def __init__(self):

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print("Loading AI image model...")

        self.model = CLIPModel.from_pretrained(
            MODEL_NAME
        ).to(self.device)

        self.processor = CLIPProcessor.from_pretrained(
            MODEL_NAME
        )

        self.model.eval()

        print("AI image model loaded successfully!")


    def load_image(self, image_path):

        image = Image.open(
            image_path
        ).convert("RGB")

        return image


    def extract_features(self, image_path):

        image = self.load_image(
            image_path
        )

        inputs = self.processor(
            images=image,
            return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():

            features = self.model.get_image_features(
                **inputs
            )

        # Normalize the embedding
        features = features / features.norm(
            p=2,
            dim=-1,
            keepdim=True
        )

        embedding = (
            features.cpu()
            .numpy()
            .astype(np.float32)
            .flatten()
        )

        return embedding


    @staticmethod
    def calculate_similarity(
        embedding1,
        embedding2
    ):

        embedding1 = np.asarray(
            embedding1,
            dtype=np.float32
        )

        embedding2 = np.asarray(
            embedding2,
            dtype=np.float32
        )

        denominator = (
            np.linalg.norm(embedding1)
            * np.linalg.norm(embedding2)
        )

        if denominator == 0:
            return 0.0

        score = np.dot(
            embedding1,
            embedding2
        ) / denominator

        return float(score)
