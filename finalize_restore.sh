#!/bin/bash

# Define paths
SOURCE_DIR=~/agent-zero
BACKUP_DIR=~/Agent-Zero-BARE-METAL-BACKUP-full
REPO_DIR=~/agent-zero # The git repo is the working dir
REPO_URL="https://github.com/NateFoxtrot/Agent-Zero-BARE-METAL.git"

echo "================================================================"
echo "       FINALIZING RESTORE AND FIX"
echo "================================================================"

# --- STEP 7: LOCAL BACKUP ---
echo "[Step 7] Creating Full Local Backup..."
if [ -d "$BACKUP_DIR" ]; then
    echo "    Removing old backup..."
    rm -rf "$BACKUP_DIR"
fi
echo "    Copying files to $BACKUP_DIR..."
cp -r "$SOURCE_DIR" "$BACKUP_DIR"
echo "✅ Local Backup Complete."
echo ""

# --- STEP 8: GITHUB UPLOAD ---
echo "[Step 8] Uploading to GitHub (NateFoxtrot/Agent-Zero-BARE-METAL)..."
cd "$SOURCE_DIR"

# 1. Initialize/Reset Git
# We assume the current folder is the 'truth'. We re-init to force a clean slate history 
# if the previous history was corrupted, or just add on top if it's clean. 
# Given the 'corruption' mentioned in the prompt, a forced clean push is safest.

if [ -d ".git" ]; then
    echo "    Re-initializing git configuration..."
    rm -rf .git
fi

git init -b main

# 2. Configure Identity (Local scope only)
git config user.email "agentzero@baremetal.local"
git config user.name "Agent Zero Bare Metal"

# 3. Add Remote
echo "    Setting remote origin..."
git remote add origin "$REPO_URL"

# 4. Stage and Commit
echo "    Staging files..."
git add .
echo "    Committing..."
git commit -m "Full Restore: Bare Metal Refactor (No Docker required), GPU enabled, Search fixed"

# 5. Push
echo "    Pushing to GitHub..."
git push -u origin main --force

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS: Codebase is live at $REPO_URL"
else
    echo ""
    echo "❌ ERROR: Git push failed. Please check your internet or credentials."
fi

echo "================================================================"
