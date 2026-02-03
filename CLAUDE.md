# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository manages n8n workflow automations using Git for version control and GitHub Actions for automated deployment to n8n Cloud. Workflows are stored as JSON files and automatically deployed when pushed to the main branch.

## Architecture

### Deployment Flow
1. Workflow JSON files are stored in `workflows/` directory
2. GitHub Actions (`.github/workflows/deploy.yml`) triggers on push to main
3. `scripts/deploy.sh` deploys workflows to n8n Cloud via REST API
4. Script matches workflows by name (updates existing or creates new)
5. Workflows are activated after deployment

### Key Components

**Deployment Script** (`scripts/deploy.sh`):
- Bash script that interfaces with n8n Cloud REST API
- Uses `N8N_BASE_URL` and `N8N_API_KEY` environment variables
- Fetches existing workflows, then creates/updates based on workflow name
- Activates workflows after deployment
- Provides colored console output for deployment status

**Workflow Structure**:
- Each workflow is a JSON file in `workflows/` directory
- Contains nodes (triggers, actions, AI agents), connections, and settings
- Credentials are referenced by ID but not included in exports (configured separately in n8n Cloud UI)
- Workflow `name` field is used to match existing workflows during updates

**Example Workflow** (`workflows/the-agentic-ai-brief.json`):
- Scheduled weekly newsletter summarizer for agentic AI news
- Uses Schedule Trigger → Python code (RSS feed URLs) → HTTP requests → AI Agent → Information Extractor → Gmail
- Requires Google Gemini API and Gmail OAuth2 credentials

## Common Commands

### Local Development

Test deployment script locally:
```bash
cp .env.example .env
# Edit .env with your N8N_BASE_URL and N8N_API_KEY
./scripts/deploy.sh
```

### Workflow Management

Add new workflow from n8n Cloud export:
```bash
mv ~/Downloads/My_Workflow.json workflows/my-workflow.json
git add workflows/my-workflow.json
git commit -m "Add new workflow: my-workflow"
git push origin main
```

Update existing workflow:
```bash
# Export updated workflow from n8n Cloud
mv ~/Downloads/Updated_Workflow.json workflows/existing-workflow.json
git add workflows/existing-workflow.json
git commit -m "Update workflow: existing-workflow"
git push origin main
```

### GitHub Actions

Manually trigger deployment:
- Go to Actions tab → Deploy n8n Workflows → Run workflow

## Important Constraints

### Credentials Management
- Workflow exports do NOT include credentials (security best practice)
- After deployment, manually configure credentials in n8n Cloud UI
- Credentials are referenced by ID in workflow JSON

### Webhook Workflows
- Due to n8n API limitation, webhook workflows need manual save after deployment
- Open workflow in n8n Cloud UI and click Save to register webhooks properly

### Deployment Matching
- Workflows are matched by the `name` field in JSON
- Changing workflow name creates a new workflow instead of updating
- Use consistent naming between local files and workflow name field

### Environment Variables
- `N8N_BASE_URL`: n8n Cloud instance URL (e.g., `https://yourinstance.app.n8n.cloud`)
- `N8N_API_KEY`: API key from n8n Cloud Settings → n8n API
- Stored as GitHub Secrets for Actions, or in `.env` for local testing
- Never commit `.env` file with real credentials

## n8n Workflow Node Types

Common node types in workflows:
- `n8n-nodes-base.scheduleTrigger`: Time-based triggers
- `n8n-nodes-base.webhook`: HTTP webhook triggers
- `n8n-nodes-base.code`: Custom JavaScript/Python code
- `n8n-nodes-base.httpRequest`: HTTP requests to external APIs
- `@n8n/n8n-nodes-langchain.agent`: AI agent with LLM
- `n8n-nodes-base.gmail`: Gmail integration
