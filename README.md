# IFT-6005 - Conversational Agent Project

A conversational agent for querying the Open Food Facts database using Hugging Face's smolagents library. 
Developed as part of IFT-6005 Integration Project at Université Laval.

## Features

- Built with Hugging Face's smolagents library
- Support for complex food-related queries
- Data visualization capabilities
- Interactive conversation history

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## Usage

```python
from src.agent import FoodAgent

# Initialize the agent
agent = FoodAgent()

# Example query
response = agent.query("Find organic products with high protein content")
```

## Project Structure

```markdown
ift-6005/
├── data/              Data used in the project
├── docs/
│   ├── data/          Information about the data used in the project
│   ├── latex/         LaTeX files for the project report
│   └── markdown/      Markdown files for the project documentation
├── notebooks/         Jupyter notebooks for data exploration
├── src/               Source code
│   └── experiments/   Experiments
├── tests/
├── requirements.txt
└── README.md
```

## Development

- Code formatting: Black
- Type checking: mypy
- Testing: pytest

## Contributing

- Fork the repository
- Create feature branch
- Commit changes
- Push to branch
- Open pull request

## License

MIT License - See LICENSE file for details.
