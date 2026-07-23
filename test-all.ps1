param(
    [string[]]$Target = @("tests")
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
$env:HEADLESS = "true"
$env:START_MAXIMIZED = "false"
$env:BROWSER_WINDOW_WIDTH = "2560"
$env:BROWSER_WINDOW_HEIGHT = "1440"
$env:VIEWPORT_WIDTH = "2560"
$env:VIEWPORT_HEIGHT = "1440"
$env:SLOW_MO_MS = "0"
$env:TEST_PAUSE_MS = "0"
$env:DEMO_HIGHLIGHT = "false"
$env:DEMO_ZOOM_PERCENT = "100"
$env:DEMO_ACTION_PAUSE_MS = "0"
$env:TRACE_ON_FAILURE = "true"
$env:VIDEO_ON_FAILURE = "false"
$env:DEMO_FINAL_SCREENSHOT = "false"

Push-Location $ProjectRoot
try {
    & $Python -m pytest -q @Target
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
