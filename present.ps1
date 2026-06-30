param(
    [int]$SlowMoMs = 180,
    [int]$PauseMs = 250,
    [int]$ActionPauseMs = 220
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ParentVenvPython = Join-Path $ProjectRoot "..\.venv\Scripts\python.exe"
$LocalVenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (Test-Path $ParentVenvPython) {
    $Python = $ParentVenvPython
} elseif (Test-Path $LocalVenvPython) {
    $Python = $LocalVenvPython
} else {
    $Python = "python"
}

$env:PYTHONIOENCODING = "utf-8"
$env:HEADLESS = "false"
$env:START_MAXIMIZED = "true"
$env:BROWSER_WINDOW_WIDTH = "2560"
$env:BROWSER_WINDOW_HEIGHT = "1440"
$env:VIEWPORT_WIDTH = "2560"
$env:VIEWPORT_HEIGHT = "1440"
$env:SLOW_MO_MS = "$SlowMoMs"
$env:TEST_PAUSE_MS = "$PauseMs"
$env:DEMO_HIGHLIGHT = "true"
$env:DEMO_ZOOM_PERCENT = "100"
$env:DEMO_ACTION_PAUSE_MS = "$ActionPauseMs"
$env:TRACE_ON_FAILURE = "true"
$env:VIDEO_ON_FAILURE = "false"
$env:DEMO_FINAL_SCREENSHOT = "true"

Push-Location $ProjectRoot
try {
    & $Python -m pytest -q tests -m demo
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
