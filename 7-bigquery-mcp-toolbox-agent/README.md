# BigQuery MCP Toolbox Agent

This project provides a toolbox agent designed to interface with Google BigQuery and related Google Cloud Platform (GCP) services, leveraging the Google ADK (Agent Development Kit) and AI Platform. The agent is intended to streamline data operations, automate workflows, and integrate advanced analytics or AI capabilities into BigQuery-powered environments.

## Features

- **BigQuery Integration:** Seamlessly interact with Google BigQuery datasets and tables.
- **AI Platform Extension:** Utilize AI Platform engines and agent capabilities for advanced analytics.
- **Cloud Storage Support:** Read from and write to Google Cloud Storage as part of your data workflows.
- **Extensible Toolbox:** Built on `toolbox-core` for modularity and reusability.

## Requirements

- Python 3.8+
- Google Cloud account with access to BigQuery, AI Platform, and Cloud Storage

Install dependencies:
```bash
pip install -r requirements.txt
```

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/rominirani/adk-projects.git
    cd adk-projects/7-bigquery-mcp-toolbox-agent
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. (Optional) Set up your Google Cloud credentials:
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
    ```

## Usage

_Usage instructions depend on the agent's interface (CLI, script, or API). Please provide additional details or see the `main.py` for entry points._

Example (if run as a script):
```bash
python main.py --help
```

## Configuration

- Ensure you have appropriate IAM roles for BigQuery, AI Platform, and Cloud Storage.
- Update any configuration files or environment variables as needed for your project.

## Contributing

Contributions are welcome! Please open issues or submit PRs for bug fixes, features, or enhancements.

## License

[MIT](../LICENSE) © 2025 rominirani

## Acknowledgements

- [Google ADK](https://github.com/google/adk)
- [Google Cloud Platform](https://cloud.google.com/)
- [toolbox-core](https://pypi.org/project/toolbox-core/)

---

_If you have code samples, command-line options, or configuration examples, please provide them for a more complete README._
