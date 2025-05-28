
#!/bin/bash

# Initialize Git repo
git init
git add .
git commit -m "Initial commit: USAJobs Skill Bridge MVP"

# Add GitHub remote (replace YOUR_TOKEN)
git remote add origin https://github.com/jasonewillis/usajobs_skill_bridge.git

# Push to GitHub (you’ll be prompted for login/token unless using credential manager)
git branch -M main
git push -u origin main
