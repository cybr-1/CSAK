# SecOps Toolkit

## Overview
SecOps Toolkit is a command-line security operations (SecOps) utility designed for cybersecurity engineers and security architects. It provides a centralized interface for running various security scripts, automating common security tasks, and enhancing cloud security posture management. The toolkit is built with Python and aims to simplify security operations by providing essential functionalities in one place.

## Target Audience
- Cybersecurity engineers and architects
- Security analysts and incident responders
- Cloud security professionals working with Azure and AWS
- Organizations looking to automate security operations

## Features
- Centralized CLI for executing security scripts
- Cloud security tools for IAM misconfigurations, storage exposure, and network visibility
- Automated vulnerability scanning integration
- Support for API integrations with Microsoft Defender XDR and Sentinel
- Extensible framework for adding custom security scripts

## Requirements
- Python 3.12+
- Pip package manager
- Required dependencies (installed automatically)
- API keys or authentication tokens for cloud integrations (if needed)

## Installation
```sh
# Clone the repository
git clone https://github.com/cybr-1/CSAK.git
cd CSAK

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the toolkit
python console.py
```

## Uninstalltion

```sh
# Navigate to the project directory and deactivate the virtual environment (if used)
deactivate  # Only if virtual environment was used

# Uninstall dependencies (optional)
pip uninstall -r requirements.txt -y

# Remove the project folder
cd ..
rm -rf CSAK
```

---

## Roadmap

### Short-Term Goals
- Implement a modular plugin system for custom scripts
- Improve logging and error handling
- Add support for more cloud security tools (AWS, Azure, GCP)

### Long-Term Goals
- Develop a web-based interface for remote execution
- Integrate AI-powered modules to enchance UX
