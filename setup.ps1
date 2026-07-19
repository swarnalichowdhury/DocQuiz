# DocQuiz setup - Windows PowerShell backup for when Git Bash isn't available.
# Run from the repo folder with:
#   powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host "=== DocQuiz setup (PowerShell) ===" -ForegroundColor Cyan

function Find-Python {
    foreach ($candidate in @("py", "python3", "python")) {
        $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($null -eq $cmd) { continue }
        try {
            $versionOutput = & $candidate --version 2>&1 | Out-String
        } catch { continue }
        if ($versionOutput -match "Python 3\.(\d+)") {
            $minor = [int]$Matches[1]
            if ($minor -ge 10) {
                return $candidate
            } else {
                Write-Host "Found $($versionOutput.Trim()) via '$candidate' - too old, need 3.10+." -ForegroundColor Yellow
            }
        }
        # No match: likely the Microsoft Store stub that prints an ad instead
        # of a version. Skip it.
    }
    return $null
}

$python = Find-Python

if ($null -eq $python) {
    Write-Host ""
    Write-Host "Python 3.10+ is required but was not found." -ForegroundColor Red
    Write-Host "Install it with ONE of these, then re-run this script:"
    Write-Host "  winget install -e --id Python.Python.3.12"
    Write-Host "  (or download from https://python.org - tick 'Add python.exe to PATH')"
    $answer = Read-Host "Try running the winget install for you now? (y/n)"
    if ($answer -eq "y") {
        winget install -e --id Python.Python.3.12
        Write-Host ""
        Write-Host "Python installed. Close this window, open a NEW PowerShell (so PATH refreshes), and re-run setup.ps1." -ForegroundColor Green
    }
    exit 1
}

Write-Host "Using $((& $python --version 2>&1 | Out-String).Trim())"

# Create venv + install deps
& $python -m venv .venv
if (-not $?) {
    Write-Host "Failed to create the virtual environment." -ForegroundColor Red
    exit 1
}
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not $?) {
    Write-Host "Dependency install failed - check your internet connection and re-run." -ForegroundColor Red
    exit 1
}

# Set up .env
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example - add your GROQ_API_KEY before running anything."
} else {
    Write-Host ".env already exists, leaving it alone."
}

Write-Host ""
Write-Host "=== Setup done ===" -ForegroundColor Green
Write-Host "Activate with:  .\.venv\Scripts\Activate.ps1"
Write-Host "(If activation is blocked, run:  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned )"
Write-Host "Then add GROQ_API_KEY to .env and run:"
Write-Host "  python starter\main.py sample_notes\python_oop_basics.pdf"
