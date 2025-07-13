# Video Reimagine 🎬

A powerful video reimagine feature that allows users to upload videos, split them into scenes, analyze content, and generate new videos based on user prompts using AI.

## ✨ Features

- **Scene Detection**: Automatic video scene splitting using PySceneDetect
- **Frame Analysis**: Detailed information extraction from video frames
- **AI Integration**: Video language model for content understanding
- **Video Generation**: AI-powered video generation and animation
- **Scene Stitching**: Intelligent transitions and audio remix capabilities

## 🏗️ Project Structure

```
gibli/
├── client/                     # All on-device code
│   ├── main.py                 # Entry-point (CLI or GUI launcher)
│   ├── splitter/               # ✅ Scene detection & splitting
│   ├── network/                # API client wrapper
│   ├── cache/                  # Local LRU caches & temp files
│   └── ui/                     # Optional front-end
├── services/                   # Cloud micro-services
│   ├── ingest/                 # Uploads, TransNet, PySceneDetect
│   ├── gen/                    # VLM + style swap + video-gen
│   └── stitch/                 # Transitions & audio remix
├── shared/                     # Shared library
├── tests/                      # Unit & integration tests
└── docs/                       # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- FFmpeg (for video processing)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tecxbro/videoreimagine.git
   cd gibli
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test scene detection**
   ```bash
   python3 client/splitter/splitter.py -i your_video.mp4 --dry-run
   ```

## 📖 Usage

### Scene Detection & Splitting

```bash
# Basic scene detection and splitting
python3 client/splitter/splitter.py -i video.mp4

# Custom parameters
python3 client/splitter/splitter.py -i video.mp4 -t 1.5 -m 10 -o my_clips/

# Dry run with statistics
python3 client/splitter/splitter.py -i video.mp4 --dry-run --stats-file stats.csv

# Verbose logging
python3 client/splitter/splitter.py -i video.mp4 -v
```

### CLI Options

- `-i, --input`: Input video file path (required)
- `-t, --threshold`: Adaptive threshold for scene detection (default: 2.0)
- `-m, --min-len`: Minimum scene length in frames (default: 15)
- `-w, --window`: Rolling average window size in frames (default: 20)
- `-o, --output`: Output directory for clips (default: clips/)
- `--dry-run`: Detect scenes but do not split video
- `--stats-file`: Save scene statistics to CSV file
- `-v, --verbose`: Enable verbose logging

## 🔧 Development

### Setting up the development environment

1. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests**
   ```bash
   pytest tests/
   ```

### Project Status

- ✅ **Scene Detection**: Complete with PySceneDetect integration
- 🔄 **Frame Analysis**: In development
- ⏳ **AI Integration**: Planned
- ⏳ **Video Generation**: Planned
- ⏳ **UI Development**: Planned

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Issues

If you encounter any issues, please check the [UPDATES.md](UPDATES.md) file for known issues and solutions, or create a new issue in the repository.

## 📞 Support

For support and questions, please open an issue in the repository or contact the development team. 