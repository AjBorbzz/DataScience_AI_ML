from dataset_loader.core.text_loader import TextDatasetLoader
from dataset_loader.core.vision_loader import VisionDatasetLoader
from dataset_loader.core.audio_loader import AudioDatasetLoader

loader_registry = {
    "text": TextDatasetLoader,
    "vision": VisionDatasetLoader,
    "audio": AudioDatasetLoader,
}
