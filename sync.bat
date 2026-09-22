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

rem A crashed or interrupted git leaves index.lock behind and blocks everything.
rem Clear it only when no rebase or merge is actually in progress.
if exist ".git\index.lock" (
  if exist ".git\rebase-merge" goto locked
  if exist ".git\rebase-apply" goto locked
  if exist ".git\MERGE_HEAD" goto locked
  echo [0/4] Removing a stale .git\index.lock left by an interrupted git...
  del /f /q ".git\index.lock"
  echo.
)
goto staging

:locked
echo [ERROR] A rebase or merge is in progress, so the lock was left alone.
echo         Finish it with: git rebase --continue   (or: git rebase --abort)
goto done

:staging
echo [1/4] Staging local changes...
git add -A
if errorlevel 1 (
  echo [ERROR] Could not stage changes.
  goto done
)
git diff --staged --quiet
if errorlevel 1 (
  git commit -m "chore: local updates"
  if errorlevel 1 (
    echo [ERROR] Commit failed.
    goto done
  )
  echo       committed.
) else (
  echo       nothing new to commit.
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
