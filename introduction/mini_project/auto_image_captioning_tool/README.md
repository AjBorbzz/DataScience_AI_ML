# BLIP2 Image Captioning Tool

A Python script that automatically generates captions for images using Salesforce's BLIP2 (Bootstrapping Language-Image Pre-training) model. This tool processes all images in a specified directory and outputs descriptive captions to a text file.

## Features

- **Batch Processing**: Automatically processes all images in a directory
- **Multiple Formats**: Supports JPG, JPEG, and PNG image formats
- **AI-Powered Captions**: Uses state-of-the-art BLIP2 model for accurate image descriptions
- **Simple Output**: Generates a clean text file with image names and corresponding captions

## Requirements

### Dependencies

```bash
pip install torch transformers pillow requests glob2
```

### System Requirements

- Python 3.7+
- CUDA-compatible GPU (recommended for faster processing)
- Sufficient RAM (model requires ~5GB of memory)

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install torch transformers pillow requests glob2
   ```
3. Update the `image_dir` variable in the script to point to your image directory

## Usage

### Basic Usage

1. **Set Image Directory**: Update the `image_dir` variable in the script:
   ```python
   image_dir = "/path/to/your/images"
   ```

2. **Run the Script**:
   ```bash
   python image_captioning.py
   ```

3. **Check Output**: The script will generate a `captions.txt` file in the same directory with the format:
   ```
   image1.jpg: A beautiful sunset over the ocean with waves crashing on the shore
   image2.png: A cat sitting on a windowsill looking outside
   ```

### Customization

#### Supported Image Formats
The script currently supports JPG, JPEG, and PNG formats. To add more formats, modify the `image_exts` list:

```python
image_exts = ["jpg", "jpeg", "png", "bmp", "tiff"]
```

#### Caption Length
Adjust the maximum caption length by modifying the `max_new_tokens` parameter:

```python
out = model.generate(**inputs, max_new_tokens=100)  # Longer captions
```

## Model Information

This script uses the **Salesforce/blip2-opt-2.7b** model:
- **Architecture**: BLIP2 with OPT-2.7B language model
- **Capabilities**: Image understanding and natural language generation
- **Performance**: High-quality captions with good semantic understanding
- **Size**: ~5GB model download on first run

## File Structure

```
your-project/
│
├── image_captioning.py     # Main script
├── captions.txt           # Generated output (created after running)
├── README.md              # This documentation
└── images/                # Your image directory
    ├── photo1.jpg
    ├── photo2.png
    └── ...
```

## Example Output

```
sunset_beach.jpg: a beautiful sunset over the ocean with palm trees in the foreground
cat_portrait.png: a close-up of a gray tabby cat with green eyes looking at the camera
mountain_landscape.jpeg: a scenic mountain range with snow-capped peaks under a blue sky
```

## Performance Notes

- **First Run**: The script will download the model (~5GB) on first execution
- **Processing Speed**: ~2-5 seconds per image on GPU, 10-30 seconds on CPU
- **Memory Usage**: Requires approximately 5GB of RAM for model loading
- **Batch Processing**: Processes images sequentially to manage memory usage

## Troubleshooting

### Common Issues

**Out of Memory Error**:
- Reduce batch size or process images individually
- Use a machine with more RAM
- Consider using a smaller BLIP2 model variant

**CUDA Out of Memory**:
- Reduce image resolution before processing
- Process fewer images at once
- Use CPU processing instead of GPU

**Missing Dependencies**:
```bash
pip install --upgrade torch transformers pillow requests
```

### Model Loading Issues
If the model fails to download or load:
- Check internet connection
- Ensure sufficient disk space (~10GB free recommended)
- Try clearing Hugging Face cache: `rm -rf ~/.cache/huggingface/`
