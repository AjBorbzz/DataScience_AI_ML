import unittest
from dataset_loader.main import load_dataset

class TestTextLoader(unittest.TestCase):
    def test_ag_news(self):
        dataset = load_dataset("text", "AG_NEWS", split="train")
        self.assertIsNotNone(dataset)

if __name__ == '__main__':
    unittest.main()
