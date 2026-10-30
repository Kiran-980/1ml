param([Parameter(Mandatory=$true)][string]$PlanPath)
$ErrorActionPreference = 'Stop'
$workspaceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$resolvedPlan = [IO.Path]::GetFullPath($PlanPath)
if (-not $resolvedPlan.StartsWith($workspaceRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Retention plan must be inside the workspace'
}
$plan = Get-Content -LiteralPath $resolvedPlan -Raw | ConvertFrom-Json
if ($plan.pruning_status -eq 'completed') { throw 'This retention plan was already applied' }
$competitionRoot = Split-Path -Parent $resolvedPlan
$current = Get-Content -LiteralPath (Join-Path $competitionRoot 'current-run.json') -Raw | ConvertFrom-Json
if ($current.run_id -ne $plan.current_run_retained) { throw 'Current run changed since planning' }

function Get-Sha256([string]$LiteralPath) {
    $stream = [IO.File]::OpenRead($LiteralPath)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-', '').ToLowerInvariant() }
    finally { $stream.Dispose(); $algorithm.Dispose() }
}

# Validate every exact file before deleting any; never recursively delete a run.
foreach ($item in $plan.weights_to_prune) {
    $runPath = [IO.Path]::GetFullPath([string]$item.run)
    $weightPath = [IO.Path]::GetFullPath([string]$item.path)
    $modelsRoot = Join-Path $runPath 'models'
    if (-not $runPath.StartsWith($workspaceRoot + '\evals\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Run outside evaluations' }
    if ((Split-Path -Leaf (Split-Path -Parent $runPath)) -ne 'runs') { throw 'Expected a run directory' }
    if ((Split-Path -Leaf $runPath) -eq $current.run_id) { throw 'Refusing to prune current model' }
    if (-not $weightPath.StartsWith($modelsRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Weight outside its models folder' }
    if ([IO.Path]::GetExtension($weightPath).ToLowerInvariant() -notin @('.joblib','.pkl','.pickle','.pt','.pth','.onnx','.safetensors')) { throw 'Not a supported weight file' }
    $file = Get-Item -LiteralPath $weightPath
    if ($file.PSIsContainer -or ($file.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Expected an ordinary weight file' }
    if ((Get-Sha256 $weightPath) -ne $item.sha256 -or $file.Length -ne $item.bytes) { throw 'Weight changed after retention planning' }
}

foreach ($group in ($plan.weights_to_prune | Group-Object run)) {
    $retentionPath = Join-Path $group.Name 'models\retention.json'
    $record = @{policy='Historical weights pruned; notebooks, source, requirements and measured result records retained';
        status='planned'; artifacts=@($group.Group); regeneration='Replay the historical notebook with its source module, recorded environment and input version; byte-identical weights are not guaranteed.'}
    $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $retentionPath -Encoding UTF8
    foreach ($item in $group.Group) { Remove-Item -LiteralPath $item.path }
    $record.status = 'pruned'
    $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $retentionPath -Encoding UTF8
}
$plan | Add-Member -NotePropertyName pruning_status -NotePropertyValue 'completed'
$plan | Add-Member -NotePropertyName pruned_at_utc -NotePropertyValue ([DateTime]::UtcNow.ToString('o'))
$plan | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $resolvedPlan -Encoding UTF8
Write-Output ('Pruned {0} historical weight files; current run retained.' -f $plan.weights_to_prune.Count)
