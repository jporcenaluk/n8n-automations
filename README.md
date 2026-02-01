# n8n Automations Repository

Version-controlled n8n workflows with automated deployment to n8n Cloud via GitHub Actions.

## Overview

This repository manages n8n workflow automations using Git for version control and GitHub Actions for automated deployment. When you push workflow changes to the main branch, they're automatically deployed to your n8n Cloud instance.

## Setup Instructions

### 1. Generate n8n API Key

1. Log in to your n8n Cloud instance
2. Navigate to **Settings** > **n8n API**
3. Click **Create API Key**
4. Copy the generated API key (you won't be able to see it again)

### 2. Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Add the following secrets:
   - `N8N_BASE_URL`: Your n8n Cloud instance URL (e.g., `https://yourinstance.app.n8n.cloud`)
   - `N8N_API_KEY`: The API key you generated in step 1

### 3. Repository Structure

```
n8n-automations/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions deployment workflow
├── workflows/
│   └── *.json                  # Your n8n workflow files
├── scripts/
│   └── deploy.sh               # Deployment script
├── .gitignore                  # Git ignore rules
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## Workflow Management

### Creating New Workflows

1. **Build in n8n Cloud UI**:
   - Create and test your workflow in n8n Cloud
   - Configure all necessary credentials in n8n

2. **Export Workflow**:
   - In n8n, open the workflow
   - Click the three-dot menu (**...**)
   - Select **Download**
   - Save the JSON file

3. **Add to Repository**:
   ```bash
   # Save the exported JSON to workflows directory
   mv ~/Downloads/My_Workflow.json workflows/my-workflow.json

   # Commit and push
   git add workflows/my-workflow.json
   git commit -m "Add new workflow: my-workflow"
   git push origin main
   ```

4. **Automatic Deployment**:
   - GitHub Actions will automatically deploy the workflow
   - Check the **Actions** tab in GitHub to monitor deployment status

### Updating Existing Workflows

1. Make changes in n8n Cloud UI
2. Export the updated workflow JSON
3. Replace the existing file in `workflows/` directory
4. Commit and push changes
5. GitHub Actions will automatically update the workflow in n8n Cloud

### Manual Deployment

You can manually trigger deployment from the GitHub Actions UI:

1. Go to **Actions** tab in your repository
2. Select **Deploy n8n Workflows**
3. Click **Run workflow**
4. Select the branch and run

## Important Notes

### Credentials

**Credentials are NOT included in workflow exports** (security best practice).

After deploying a workflow, you'll need to:
1. Open the workflow in n8n Cloud UI
2. Configure any required credentials
3. Save the workflow

Document required credentials in your workflow's description or commit message.

### Webhook Workflows

Due to a known n8n API limitation, webhook-based workflows may need a manual save after API deployment:

1. Deploy the workflow via GitHub Actions
2. Open the workflow in n8n Cloud UI
3. Click **Save** (even without changes)
4. This ensures webhooks are properly registered

### Version Control Benefits

- **Change History**: Full audit trail of workflow modifications
- **Rollback**: Easily revert to previous versions
- **Collaboration**: Team members can review changes via Pull Requests
- **Backup**: Workflows are safely stored in Git
- **Documentation**: Commit messages explain why changes were made

## Workflows

### the-agentic-ai-brief

AI-powered newsletter summarizer for software engineers. Aggregates and summarizes key developments in agentic AI.

**Status**: Template created, needs customization in n8n Cloud UI

**Required Credentials**:
- To be configured based on your specific implementation

## Troubleshooting

### Deployment Fails

1. **Check GitHub Secrets**: Verify `N8N_BASE_URL` and `N8N_API_KEY` are correctly configured
2. **API Key Validity**: Ensure your API key hasn't expired
3. **Instance URL**: Confirm your n8n Cloud instance URL is correct (include `https://`)
4. **Workflow JSON**: Validate JSON syntax (use a JSON validator)

### Workflow Not Activating

1. Check the GitHub Actions log for error messages
2. Verify the workflow activated in n8n Cloud UI
3. For webhook workflows, manually save in n8n UI after deployment
4. Ensure all required credentials are configured

### Changes Not Deploying

1. Confirm you pushed to the `main` branch
2. Check the **Actions** tab for workflow run status
3. Review the deployment logs for errors

## Local Development

To test deployment scripts locally:

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env

# Run deployment script
./scripts/deploy.sh
```

**Warning**: Never commit your `.env` file with real credentials!

## Contributing

1. Create a feature branch
2. Make your changes
3. Test in your n8n Cloud instance
4. Submit a Pull Request
5. After review, merge to main for automatic deployment

## Resources

- [n8n Documentation](https://docs.n8n.io/)
- [n8n API Reference](https://docs.n8n.io/api/)
- [n8n Community Forum](https://community.n8n.io/)
- [Workflow Export/Import Guide](https://docs.n8n.io/workflows/export-import/)
