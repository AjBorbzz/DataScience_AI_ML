from dataset_loader.config.registry import loader_registry

def load_dataset(domain: str, name: str, **kwargs):
    loader_cls = loader_registry.get(domain)
    if not loader_cls:
        raise ValueError(f"Unsupported domain: {domain}")
    return loader_cls(domain, name, **kwargs).load()

# Usage
dataset = load_dataset("text", "AG_NEWS", split="train")
for label, text in dataset:
    print(label, text)
    break
