# blog/ai_utils.py

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

# Load the BLIP model and processor once
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base",use_fast=False)
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_caption_and_hashtags(image_path):
    image = Image.open(image_path).convert('RGB')
# blog/ai_utils.py

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_blip_model():
    """
    Load the BLIP model and processor only once using caching.
    """
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base", use_fast=True)
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return processor, model

def generate_caption_and_hashtags(image_path):
    """
    Generates an image caption and related hashtags using BLIP.
    """
    try:
        image = Image.open(image_path).convert('RGB')
        processor, model = get_blip_model()

        inputs = processor(image, return_tensors="pt")
        outputs = model.generate(**inputs)

        caption = processor.decode(outputs[0], skip_special_tokens=True)
        hashtags = suggest_hashtags(caption)

        logger.info(f"Generated Caption: {caption}")
        logger.info(f"Hashtags: {hashtags}")
        logger.info(f"Image path for captioning: {image_path}")

        return caption, hashtags

    except Exception as e:
        logger.error(f"Failed to generate caption for {image_path}: {str(e)}")
        return "No caption generated", []

def suggest_hashtags(caption):
    """
    Extracts keywords from caption to suggest simple hashtags.
    """
    keywords = [word.lower() for word in caption.split() if len(word) > 3]
    hashtags = [f"#{word}" for word in keywords[:5]]
    return hashtags

    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)

    hashtags = suggest_hashtags(caption)
    return caption, hashtags

def suggest_hashtags(caption):
    keywords = [word.lower() for word in caption.split() if len(word) > 3]
    hashtags = [f"#{word}" for word in keywords[:5]]
    return hashtags
