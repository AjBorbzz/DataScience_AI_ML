from torchtext.datasets import AG_NEWS, IMDB, TREC
from .base import DatasetLoader

dataset_map = {
    "AG_NEWS": AG_NEWS,
    "IMDB": IMDB,
    "TREC": TREC
}

class TextDatasetLoader(DatasetLoader):
    def load(self):
        dataset_cls = dataset_map.get(self.name)
        if dataset_cls is None:
            raise ValueError(f"{self.name} is not supported.")
        return dataset_cls(split=self.kwargs.get("split", "train"))
