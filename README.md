# 🕰️ WebPastMachine

![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📖 Description

WebPastMachine is a powerful tool that lets you explore the history of any website through the Internet Archive's Wayback Machine. It helps you discover all archived URLs for a domain, analyze the types of content that were archived, and export the results for further analysis.

## ✨ Features

- 🔍 Search for all archived URLs of any domain
- 📊 Analyze file types and their distribution
- 🔎 Filter results by file extension
- 💾 Export results to a file
- ⚡ Fast and efficient processing
- 🛠️ Easy to use command-line interface

## 🚀 Installation

1. Clone this repository:
```bash
git clone https://github.com/Shac0x/WebPastMachine
cd WebPastMachine
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Basic Usage

Search for all archived URLs of a domain:
```bash
python WebPastMachine.py example.com
```

### Advanced Options

1. Filter by file extension:
```bash
python WebPastMachine.py example.com -e pdf
```

2. Export results to a file:
```bash
python WebPastMachine.py example.com -o results.txt
```

3. Combine filtering and export:
```bash
python WebPastMachine.py example.com -e pdf -o pdfs.txt
```

### 📋 Command Line Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| domain | The domain to search (required) | example.com |
| -e, --extension | Filter by file extension | -e pdf |
| -o, --output | Output file to save results | -o results.txt |
| -h, --help | Show help message | -h |

## 📝 Output Format

### Console Output
```
Searching archived URLs for example.com...

Analysis of file types found:
--------------------------------------------------
*.html: 150 files
*.php: 45 files
*.jpg: 30 files
*.pdf: 25 files
*.js: 20 files

Total unique URLs found: 270

URL: https://example.com/page.html
First capture: 2010-01-15 14:25:10
Archive link: http://web.archive.org/web/20100115142510/https://example.com/page.html
------------------------------------
```

### File Output
The exported file will contain all URLs with their capture dates and archive links in a clean, readable format.

## 🎯 Use Cases

- 📚 Research: Investigate the history of websites
- 🔒 Security: Find old versions of sensitive pages
- 🎨 Design: Track website design evolution
- 📊 Analysis: Study content distribution over time
- 🔍 Discovery: Find lost or removed content

## ⚙️ Technical Details

- Uses the Wayback Machine CDX API
- Implements efficient URL deduplication
- Handles rate limiting and timeouts
- Provides meaningful error messages
- Supports Unicode domains and paths

## 🐛 Error Handling

The tool handles various error scenarios:
- Invalid domains
- Network connection issues
- API response errors
- File writing permissions
- Invalid file extensions


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- Internet Archive for providing the Wayback Machine