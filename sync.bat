@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo   MyNews - sync with GitHub
echo ==========================================
echo.

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  echo [ERROR] This folder is not a git repository.
  goto done
)

echo [1/4] Staging local changes...
git add -A
git diff --staged --quiet
if errorlevel 1 (
  git commit -m "fix: publishedAt output, source links and mobile tweaks"
  if errorlevel 1 (
    echo [ERROR] Commit failed.
    goto done
  )
  echo       committed.
) else (
  echo       nothing to commit.
)
echo.

echo [2/4] Fetching from GitHub...
git fetch origin
if errorlevel 1 (
  echo [ERROR] Could not reach GitHub. Check your sign-in and network.
  goto done
)
echo.

echo [3/4] Rebasing onto origin/main...
git pull --rebase origin main
if errorlevel 1 (
  echo [ERROR] Rebase stopped. Resolve conflicts, then run: git rebase --continue
  goto done
)
echo.

echo [4/4] Pushing to GitHub...
git push origin main
if errorlevel 1 (
  echo [ERROR] Push failed.
  goto done
)
echo.
echo ==========================================
echo   Done. Local and GitHub are in sync.
echo ==========================================
git log --oneline -3

:done
echo.
pause
endlocal
