param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('execute_notebook', 'verify_bundle')]
    [string]$Operation
)
$ErrorActionPreference = 'Stop'
$runRoot = Split-Path -Parent $PSScriptRoot
$runTemp = Join-Path $PSScriptRoot 'runtime'
New-Item -ItemType Directory -Force -Path $runTemp | Out-Null
$env:TEMP = $runTemp
$env:TMP = $runTemp
Set-Location -LiteralPath $runRoot
& (Join-Path $PSScriptRoot 'environment/Scripts/python.exe') -X utf8 (Join-Path $PSScriptRoot 'run_checks.py') $Operation
exit $LASTEXITCODE
