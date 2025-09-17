#!/bin/bash
set -euo pipefail

# Ignition 8.3 Git Integration Setup
# This script initializes git repositories for Ignition configuration and project version control

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

CONFIG_DIR="${ROOT_DIR}/ignition-config"
PROJECTS_DIR="${ROOT_DIR}/ignition-projects"

echo "🔧 Ignition 8.3 Git Integration Setup"
echo "====================================="
echo "Root directory: ${ROOT_DIR}"
echo "Config directory: ${CONFIG_DIR}"
echo "Projects directory: ${PROJECTS_DIR}"
echo ""

# Function to setup git for a directory
setup_git_repo() {
    local dir=$1
    local repo_name=$2
    
    echo "📁 Setting up git repository for ${repo_name}..."
    
    if [ ! -d "$dir" ]; then
        echo "⚠️  Directory ${dir} does not exist, creating..."
        mkdir -p "$dir"
    fi
    
    cd "$dir"
    
    # Initialize git if not already initialized
    if [ ! -d ".git" ]; then
        echo "🔧 Initializing git repository..."
        git init
        
        # Set up git config from environment variables
        if [ ! -z "${GIT_AUTHOR_NAME:-}" ]; then
            git config user.name "${GIT_AUTHOR_NAME}"
        else
            git config user.name "Ignition System"
        fi
        
        if [ ! -z "${GIT_AUTHOR_EMAIL:-}" ]; then
            git config user.email "${GIT_AUTHOR_EMAIL}"
        else
            git config user.email "ignition@localhost"
        fi
        
        echo "✅ Git repository initialized for ${repo_name}"
    else
        echo "ℹ️  Git repository already exists for ${repo_name}"
    fi
    
    # Create or update .gitignore
    create_gitignore "$repo_name"
    
    # Create initial commit if repository is empty
    if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
        echo "📝 Creating initial commit..."
        git add .
        git commit -m "Initial commit: ${repo_name} setup for Ignition 8.3

- Added .gitignore for ${repo_name}
- Ready for version control
- JSON-based configuration storage"
        echo "✅ Initial commit created"
    fi
    
    cd "$ROOT_DIR"
}

# Function to create appropriate .gitignore files
create_gitignore() {
    local repo_type=$1
    
    case "$repo_type" in
        "projects")
            cat > .gitignore << 'EOF'
# Ignition Projects .gitignore

# Python bytecode
*.pyc
*.pyo
__pycache__/

# System files
.DS_Store
Thumbs.db

# Ignition specific temporary files
*.tmp
*.bak
*.backup
resource.lock
*.idb

# Runtime generated files
jar-cache/
logs/
.container-init.conf
.context.tmp

# Local development files
local/
dev/
*.local

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Node modules (if using web dev)
node_modules/
EOF
            ;;
        "configuration")
            cat > .gitignore << 'EOF'
# Ignition Configuration .gitignore

# Sensitive configuration files
*.key
*.p12
*.pfx
*.jks
keystore/
certificates/

# Runtime files
*.lock
*.tmp
cache/
logs/

# System files
.DS_Store
Thumbs.db

# Database files
*.idb
*.db
*.sqlite

# Local overrides
local/
dev/
*.local
EOF
            ;;
    esac
}

# Function to create automation hooks
create_git_hooks() {
    echo "🔧 Creating git hooks for automation..."
    
    # Create pre-commit hook for projects
    if [ -d "${PROJECTS_DIR}/.git" ]; then
        cat > "${PROJECTS_DIR}/.git/hooks/pre-commit" << 'EOF'
#!/bin/bash
# Pre-commit hook for Ignition projects

echo "🔍 Pre-commit checks for Ignition projects..."

# Check for sensitive data
if grep -r "password\|secret\|key" --include="*.json" . | grep -v ".git"; then
    echo "❌ Potential sensitive data found in commit!"
    echo "Please review and remove before committing."
    exit 1
fi

# Validate JSON files
find . -name "*.json" -type f | while read -r file; do
    if ! python3 -m json.tool "$file" > /dev/null 2>&1; then
        echo "❌ Invalid JSON in file: $file"
        exit 1
    fi
done

echo "✅ Pre-commit checks passed"
EOF
        chmod +x "${PROJECTS_DIR}/.git/hooks/pre-commit"
        echo "✅ Pre-commit hook created for projects"
    fi
}

# Function to create version control workflow documentation
create_workflow_docs() {
    echo "📝 Creating version control workflow documentation..."
    
    cat > "${ROOT_DIR}/GIT-WORKFLOW.md" << 'EOF'
# Ignition 8.3 Git Workflow

This document describes the git workflow for managing Ignition configurations and projects.

## Repository Structure

```
├── ignition-config/     # Gateway configuration (JSON files)
├── ignition-projects/   # Project files (JSON format)
└── ignition-backups/    # Automated backups
```

## Workflow

### Daily Development
1. Make changes in Ignition Designer
2. Changes are automatically saved as JSON files
3. Review changes: `git diff`
4. Stage changes: `git add .`
5. Commit: `git commit -m "Descriptive message"`

### Project Deployment
1. Create feature branch: `git checkout -b feature/new-hmi`
2. Develop and test in development mode
3. Commit changes incrementally
4. Merge to main: `git checkout main && git merge feature/new-hmi`
5. Tag release: `git tag -a v1.0.0 -m "Production release"`

### Configuration Management
1. Gateway configs are in `ignition-config/`
2. Automatic backups before major changes
3. Use deployment modes for environment-specific configs
4. Review config changes carefully before committing

## Best Practices

### Commit Messages
- Use descriptive, concise messages
- Start with action verb (Add, Update, Fix, Remove)
- Include issue/ticket numbers if applicable

Examples:
```
Add new tank level monitoring view
Update database connection settings for production
Fix alarm notification configuration
Remove deprecated tag references
```

### Branching Strategy
- `main` branch for production-ready code
- `develop` branch for integration testing
- Feature branches for new development
- Hotfix branches for urgent production fixes

### File Management
- Don't commit sensitive data (passwords, keys)
- Use .gitignore for temporary files
- Commit logical chunks of changes
- Test thoroughly before merging to main

## Useful Commands

```bash
# Check status
git status

# View changes
git diff
git diff --staged

# Stage and commit
git add .
git commit -m "Your message"

# View history
git log --oneline
git log --graph --all

# Create and switch branches
git checkout -b feature/branch-name
git checkout main

# Tag releases
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin --tags

# Backup and restore
./scripts/backup-ignition.sh
```

## Automation Features

- Pre-commit hooks validate JSON files
- Automatic .gitignore management
- Backup integration with git
- Deployment mode integration

## Troubleshooting

### Large File Issues
If you encounter large files that shouldn't be versioned:
```bash
git rm --cached large-file.log
echo "large-file.log" >> .gitignore
git commit -m "Remove large file from tracking"
```

### Merge Conflicts
For JSON configuration conflicts:
1. Review conflicting files carefully
2. Use Ignition Designer to resolve configuration issues
3. Test thoroughly before committing resolution

### Reset to Previous Version
```bash
# Soft reset (keeps changes in working directory)
git reset --soft HEAD~1

# Hard reset (discards changes)
git reset --hard HEAD~1
```
EOF

    echo "✅ Workflow documentation created at GIT-WORKFLOW.md"
}

# Main execution
main() {
    echo "🚀 Starting git integration setup..."
    
    # Setup git repositories
    setup_git_repo "$PROJECTS_DIR" "projects"
    setup_git_repo "$CONFIG_DIR" "configuration"
    
    # Create git hooks
    create_git_hooks
    
    # Create workflow documentation
    create_workflow_docs
    
    echo ""
    echo "🎉 Git integration setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Review the GIT-WORKFLOW.md file for usage guidelines"
    echo "2. Create your first Ignition project and watch it appear in git"
    echo "3. Use 'git status' in project directories to see changes"
    echo "4. Commit changes regularly with descriptive messages"
    echo ""
    echo "Git repositories created:"
    echo "- ${PROJECTS_DIR}"
    echo "- ${CONFIG_DIR}"
    echo ""
}

main "$@"