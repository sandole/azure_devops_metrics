# Azure DevOps Impact Metrics

A Python script that analyzes your contributions across Azure DevOps repositories, providing insights into commits, pull requests, and work items for performance reviews and impact assessment.

## Features

- **Commit Analysis**: Track your commits across all repositories in an organization or specific project
- **Pull Request Metrics**: Monitor pull request activity (currently shows all PRs for reference)
- **Work Item Tracking**: View work items assigned to you
- **Flexible Filtering**: Filter by specific projects, time periods, and user email
- **Corporate-Friendly**: Supports environments with SSL verification disabled

## Prerequisites

- Python 3.6 or higher
- Azure DevOps Personal Access Token (PAT)
- Network access to your Azure DevOps organization

## Setup

1. **Create a virtual environment**:
   ```bash
   python3 -m venv azure_metrics_env
   ```

2. **Activate the virtual environment**:
   ```bash
   source azure_metrics_env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install requests
   ```

## Usage

### Basic Usage

```bash
python3 azure_devops_metrics.py --organization "your-org" --pat "your-pat-token" --email "your.email@company.com"
```

### Command Line Options

| Option | Short | Required | Description |
|--------|-------|----------|-------------|
| `--organization` | `-o` | ✅ | Azure DevOps organization name |
| `--pat` | `-p` | ✅ | Personal Access Token |
| `--email` | `-e` | | Your email address for filtering commits and work items |
| `--project` | `-pr` | | Specific project name (optional, analyzes all projects if not specified) |
| `--days` | `-d` | | Number of days to look back (default: 90) |
| `--no-ssl-verify` | | | Disable SSL certificate verification (for corporate firewalls) |

## Getting Your Personal Access Token (PAT)

1. Go to your Azure DevOps organization
2. Click on your profile picture → Personal access tokens
3. Click "New Token"
4. Set appropriate scopes:
   - **Code**: Read (for repository access)
   - **Work Items**: Read (for work item tracking)
   - **Project and Team**: Read (for project information)
5. Copy the generated token and use it with the `--pat` parameter

## Sample Output

```
🔍 Analyzing Azure DevOps impact for the last 90 days...
🔗 Testing connectivity to Azure DevOps...
✅ Successfully connected! Found 15 projects.
👤 Filtering by email: your.email@company.com
============================================================

📁 Project: Middleware
  Found 8 repositories
  📂 api-gateway: 12 commits, 3 PRs (all users)
  📂 user-service: 8 commits, 2 PRs (all users)
  📋 Work Items assigned to you: 5

============================================================
📊 SUMMARY METRICS
============================================================
📝 Your Commits: 20
🔄 Total Pull Requests (all users): 5
📋 Work Items assigned to you: 5

🏆 Most Active Repositories:
  • Middleware/api-gateway: 12 commits, 3 PRs
  • Middleware/user-service: 8 commits, 2 PRs

⏰ Analysis period: Last 90 days
📅 Generated on: 2025-01-26 14:30:22
```