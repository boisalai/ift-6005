# Installation

Follow these instructions to set up your local development environment using Git and connect it to your GitHub repository.

## Prerequisites
- Python 3.10 or higher
- Git
- GitHub account
- Anthropic API key (get it from https://console.anthropic.com/)

## Setup Steps

1. Clone the GitHub repository:
```bash
git clone https://github.com/boisalai/ift-6005.git
cd ift-6005
```

2. Create and activate a Python virtual environment:

On macOS/Linux:
```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root directory:
```bash
touch .env  # On macOS/Linux
# OR manually create .env file on Windows
```

5. Add your Anthropic API key to the `.env` file:
```text
ANTHROPIC_API_KEY=sk-ant-xxxx...  # Replace with your actual API key
```

**Important**: Never commit your `.env` file to version control. The `.gitignore` file should already be configured to exclude it.

## Verify Installation

To verify your installation, run the test suite (if available):
```bash
python -m pytest
```

## Troubleshooting

If you encounter any issues:
- Ensure you have the correct Python version installed
- Make sure your virtual environment is activated (you should see `(.venv)` in your terminal prompt)
- Try updating pip before installing requirements: `pip install --upgrade pip`
- Verify your `.env` file exists and contains your API key
- Check that the API key is properly formatted
