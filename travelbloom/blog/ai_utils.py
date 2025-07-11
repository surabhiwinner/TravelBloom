# blog/ai_utils.py

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

# Load the BLIP model and processor once
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_caption_and_hashtags(image_path):
    image = Image.open(image_path).convert('RGB')

    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)

    hashtags = suggest_hashtags(caption)
    return caption, hashtags

def suggest_hashtags(caption):
    keywords = [word.lower() for word in caption.split() if len(word) > 3]
    hashtags = [f"#{word}" for word in keywords[:5]]
    return hashtags
