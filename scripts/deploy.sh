#!/bin/bash

# n8n Workflow Deployment Script
# Deploys workflows from the workflows/ directory to n8n Cloud

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WORKFLOWS_DIR="./workflows"
N8N_API_URL="${N8N_BASE_URL}/api/v1"

# Validate environment variables
if [ -z "$N8N_BASE_URL" ]; then
    echo -e "${RED}Error: N8N_BASE_URL environment variable is not set${NC}"
    exit 1
fi

if [ -z "$N8N_API_KEY" ]; then
    echo -e "${RED}Error: N8N_API_KEY environment variable is not set${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}n8n Workflow Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Base URL: ${N8N_BASE_URL}"
echo -e "Workflows directory: ${WORKFLOWS_DIR}"
echo ""

# Function to get all existing workflows
get_existing_workflows() {
    curl -s -X GET \
        "${N8N_API_URL}/workflows" \
        -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
        -H "Accept: application/json"
}

# Function to create a new workflow
create_workflow() {
    local workflow_file=$1
    local workflow_data=$2

    echo -e "${YELLOW}Creating new workflow from ${workflow_file}...${NC}"

    response=$(curl -s -w "\n%{http_code}" -X POST \
        "${N8N_API_URL}/workflows" \
        -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$workflow_data")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        workflow_id=$(echo "$body" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
        echo -e "${GREEN}✓ Workflow created successfully (ID: ${workflow_id})${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to create workflow (HTTP ${http_code})${NC}"
        echo "$body"
        return 1
    fi
}

# Function to update an existing workflow
update_workflow() {
    local workflow_id=$1
    local workflow_file=$2
    local workflow_data=$3

    echo -e "${YELLOW}Updating existing workflow (ID: ${workflow_id})...${NC}"

    response=$(curl -s -w "\n%{http_code}" -X PUT \
        "${N8N_API_URL}/workflows/${workflow_id}" \
        -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$workflow_data")

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✓ Workflow updated successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to update workflow (HTTP ${http_code})${NC}"
        echo "$body"
        return 1
    fi
}

# Function to activate a workflow
activate_workflow() {
    local workflow_id=$1

    echo -e "${YELLOW}Activating workflow...${NC}"

    response=$(curl -s -w "\n%{http_code}" -X PATCH \
        "${N8N_API_URL}/workflows/${workflow_id}" \
        -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d '{"active": true}')

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}✓ Workflow activated successfully${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠ Failed to activate workflow (HTTP ${http_code})${NC}"
        echo "$body"
        return 0  # Don't fail deployment if activation fails
    fi
}

# Get existing workflows
echo -e "${BLUE}Fetching existing workflows from n8n Cloud...${NC}"
existing_workflows=$(get_existing_workflows)

if [ -z "$existing_workflows" ]; then
    echo -e "${YELLOW}⚠ Could not fetch existing workflows. Will attempt to create all workflows as new.${NC}"
fi

# Process each workflow file
workflow_count=0
success_count=0
failure_count=0

for workflow_file in "${WORKFLOWS_DIR}"/*.json; do
    if [ ! -f "$workflow_file" ]; then
        echo -e "${YELLOW}No workflow files found in ${WORKFLOWS_DIR}${NC}"
        break
    fi

    workflow_count=$((workflow_count + 1))
    filename=$(basename "$workflow_file")

    echo ""
    echo -e "${BLUE}----------------------------------------${NC}"
    echo -e "${BLUE}Processing: ${filename}${NC}"
    echo -e "${BLUE}----------------------------------------${NC}"

    # Read workflow file
    workflow_data=$(cat "$workflow_file")
    workflow_name=$(echo "$workflow_data" | grep -o '"name":"[^"]*' | head -1 | cut -d'"' -f4)

    if [ -z "$workflow_name" ]; then
        echo -e "${RED}✗ Could not extract workflow name from ${filename}${NC}"
        failure_count=$((failure_count + 1))
        continue
    fi

    echo -e "Workflow name: ${workflow_name}"

    # Check if workflow exists
    existing_id=$(echo "$existing_workflows" | grep -o "\"name\":\"${workflow_name}\"" -A 100 | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

    if [ -n "$existing_id" ]; then
        echo -e "Found existing workflow with ID: ${existing_id}"
        if update_workflow "$existing_id" "$filename" "$workflow_data"; then
            activate_workflow "$existing_id"
            success_count=$((success_count + 1))
        else
            failure_count=$((failure_count + 1))
        fi
    else
        echo -e "No existing workflow found with name: ${workflow_name}"
        if create_workflow "$filename" "$workflow_data"; then
            # Get the newly created workflow ID
            new_workflows=$(get_existing_workflows)
            new_id=$(echo "$new_workflows" | grep -o "\"name\":\"${workflow_name}\"" -A 100 | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)
            if [ -n "$new_id" ]; then
                activate_workflow "$new_id"
            fi
            success_count=$((success_count + 1))
        else
            failure_count=$((failure_count + 1))
        fi
    fi
done

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Deployment Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total workflows processed: ${workflow_count}"
echo -e "${GREEN}Successful: ${success_count}${NC}"
echo -e "${RED}Failed: ${failure_count}${NC}"
echo ""

if [ $failure_count -gt 0 ]; then
    echo -e "${YELLOW}⚠ Some workflows failed to deploy. Check the logs above for details.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ All workflows deployed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Important reminders:${NC}"
    echo -e "1. Configure credentials for your workflows in n8n Cloud UI"
    echo -e "2. For webhook workflows, open and save them in the UI to register webhooks"
    echo -e "3. Verify workflows are active in your n8n Cloud instance"
fi
