@echo off
echo 🔧 Updating Docker credentials and pushing to Git...

cd /d "%~dp0"

echo 📝 Adding all changes...
git add .

echo 💾 Committing changes...
git commit -m "Update Docker Hub credentials and fix CI/CD authentication"

echo 🚀 Pushing to GitHub...
git push origin main

echo.
echo ✅ Successfully pushed to GitHub!
echo.
echo ============================================================
echo 🔐 NEXT STEP: Add these secrets to your GitHub repository
echo ============================================================
echo 1. Go to: https://github.com/blackholeinfiverse54-creator/Ai-Agent
echo 2. Navigate to: Settings → Secrets and variables → Actions
echo 3. Click 'New repository secret' and add:
echo    - Name: DOCKER_USERNAME
echo    - Value: ashmitpandey299
echo    - Name: DOCKER_PASSWORD  
echo    - Value: YOUR_DOCKER_TOKEN_HERE
echo ============================================================
echo.
echo 🎉 All done! Your CI/CD pipeline will work once you add the GitHub secrets.

pause