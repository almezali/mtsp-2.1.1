
     ███╗   ███╗████████╗███████╗██████╗"     
     ████╗ ████║╚══██╔══╝██╔════╝██╔══██╗"     
     ██╔████╔██║   ██║   ███████╗██████╔╝"     
     ██║╚██╔╝██║   ██║   ╚════██║██╔═══╝"     
     ██║ ╚═╝ ██║   ██║   ███████║██║"          
     ╚═╝     ╚═╝   ╚═╝   ╚══════╝╚═╝"          
                             
# MTSP - Multimedia Terminal Soundtrack Player 🎵

## Overview

MTSP (Multimedia Terminal Soundtrack Player) is a powerful, lightweight, and feature-rich command-line music player for Linux and Unix-like systems. Designed for music enthusiasts who prefer terminal-based applications, MTSP offers a seamless and intuitive way to manage and play your music library.

## Features

- 📂 Music Library Management
  - Scan and index music directories automatically
  - Support for multiple audio formats (MP3, WAV, FLAC, OGG, M4A)
  - Metadata extraction (artist, album, duration)

- 🎧 Advanced Playback Controls
  - Play, pause, resume, stop
  - Next and previous track navigation
  - Shuffle playlist
  - Random track selection

- 🔍 Flexible Track Search and Listing
  - Search tracks by filename, artist, or album
  - List tracks with sorting options (filename, artist, album, duration)
  - Pagination and track limiting

- 💾 SQLite Database Backend
  - Persistent music library storage
  - Efficient track metadata management

- 🖥️ Interactive Command-Line Interface
  - Simple, user-friendly shell interface
  - Comprehensive help menu
  - Error handling and user guidance

## Requirements

### Dependencies

- Python 3.7+
- `mpv` media player
- `mutagen` Python library
- `sqlite3` (typically included with Python)

### Supported Operating Systems
- Linux distributions (Ubuntu, Fedora, Debian, Arch)
- macOS
- BSD-based systems
- Windows (with Windows Subsystem for Linux or Cygwin)

## Installation

### 1. Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip mpv
```

#### Fedora
```bash
sudo dnf install python3 python3-pip mpv
```

#### Arch Linux
```bash
sudo pacman -S python python-pip mpv
```

#### macOS (using Homebrew)
```bash
brew install python mpv
```

### 2. Clone the Repository
```bash
git clone https://github.com/almezali/mtsp.git
cd mtsp
```

### 3. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

## Usage

### Basic Commands

- `scan`: Scan music library
- `list`: List tracks (with optional sorting)
- `play [id]`: Play tracks
- `pause`: Pause playback
- `resume`: Resume playback
- `next`: Next track
- `prev`: Previous track
- `search [term]`: Search tracks
- `help`: Show available commands

### Examples

```bash
# Scan music library
python3 mtsp-music-player.py -d ~/Music

# Play tracks from a specific directory
python3 mtsp-music-player.py --dir /path/to/music

# Inside the shell
mtsp> scan
mtsp> list artist DESC
mtsp> play
mtsp> search Beatles
```

## Configuration

- Music library location defaults to `~/Music`
- Configuration and database stored in `~/.shell_music_player/`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

[FREE].

## Roadmap

- [ ] Add playlist creation and management
- [ ] Implement volume control
- [ ] Create configuration file support
- [ ] Add more audio metadata display options

## Contact

m.almezali - mzmcsmzm@gmail.com

Project Link: [https://github.com/almezali/mtsp-2.1.1](https://github.com/almezali/mtsp-2.1.1)
