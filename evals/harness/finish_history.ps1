param([Parameter(Mandatory=$true)][string]$ManifestPath)
$ErrorActionPreference = 'Stop'
function Read-Sha256([string]$Path) {
    $stream = [IO.File]::OpenRead($Path)
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
    finally { $stream.Dispose(); $algorithm.Dispose() }
}
$manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
$datasetRoot = [IO.Path]::GetFullPath($manifest.dataset)
$projectRoot = [IO.Path]::GetFullPath($manifest.project)
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$datasetPrefix = $repoRoot.TrimEnd('\') + '\evals\kaggle\'
if (-not $datasetRoot.StartsWith($datasetPrefix,[StringComparison]::OrdinalIgnoreCase)) { throw 'Dataset outside evaluation workspace' }
$parent = Split-Path -Parent $projectRoot
if ((Split-Path -Parent $parent) -ne $datasetRoot -or (Split-Path -Leaf $parent) -notin @('work','runs')) { throw 'Invalid project cleanup target' }
if ($manifest.state -ne 'prepared; original project not removed') { throw 'Manifest is not a fresh prepared migration' }
$runId = Split-Path -Leaf $projectRoot
$archiveRoot = [IO.Path]::GetFullPath($manifest.notebooks)
if ($archiveRoot -ne (Join-Path $datasetRoot "evaluator\$runId\notebook-history")) { throw 'Unexpected notebook archive path' }
$knownPaths = @($manifest.files.PSObject.Properties.Name)
foreach ($actual in Get-ChildItem -LiteralPath $projectRoot -Recurse -File -Force) {
    $relative = $actual.FullName.Substring($projectRoot.Length+1).Replace('\','/')
    $parts = $relative.Split('/')
    if (@($parts | Where-Object { $_ -in @('environment','runtime','__pycache__','.ipynb_checkpoints','cache') }).Count -gt 0 -or $actual.Extension -eq '.pyc') { continue }
    if ($relative -notin $knownPaths) { throw "New source file since archive: $relative" }
}
foreach ($entry in $manifest.files.PSObject.Properties) {
    $original = [IO.Path]::GetFullPath((Join-Path $projectRoot $entry.Name))
    if (-not $original.StartsWith($projectRoot.TrimEnd('\')+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Escaping original file' }
    if ((Read-Sha256 $original) -ne $entry.Value.sha256) { throw "Source changed since archive: $($entry.Name)" }
    if ($entry.Value.file) {
        $retained = [IO.Path]::GetFullPath((Join-Path $datasetRoot $entry.Value.file))
        if (-not $retained.StartsWith($repoRoot.TrimEnd('\')+'\evals\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Retained file outside evaluation workspace' }
        if ((Read-Sha256 $retained) -ne $entry.Value.sha256) { throw "Retained evidence mismatch: $($entry.Name)" }
    }
}
# Remove read-only hard-link aliases without changing the shared file's
# attributes. Remove-Item -Force clears those attributes on every alias.
Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
public static class HistoryAliasDeletion {
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  static extern IntPtr CreateFile(string name, uint access, uint share, IntPtr security, uint disposition, uint flags, IntPtr template);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern bool SetFileInformationByHandle(IntPtr handle, int kind, ref uint info, uint size);
  [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr handle);
  public static void Delete(string path) {
    var handle=CreateFile(path, 0x10000, 7, IntPtr.Zero, 3, 0x00200000, IntPtr.Zero);
    if (handle==new IntPtr(-1)) throw new Win32Exception(Marshal.GetLastWin32Error());
    try {
      uint flags=1|2|16; // DELETE | POSIX_SEMANTICS | IGNORE_READONLY_ATTRIBUTE
      if (!SetFileInformationByHandle(handle,21,ref flags,4)) throw new Win32Exception(Marshal.GetLastWin32Error());
    } finally { CloseHandle(handle); }
  }
}
'@
foreach ($file in Get-ChildItem -LiteralPath $projectRoot -Recurse -File -Force) {
    if (($file.Attributes -band [IO.FileAttributes]::ReadOnly) -ne 0) { [HistoryAliasDeletion]::Delete($file.FullName) }
}
# Exact project target is checked above. Caller must only finish completed runs.
Remove-Item -LiteralPath $projectRoot -Recurse -Force
$historyRoot = Join-Path $datasetRoot "runs\$runId"
if (Test-Path -LiteralPath $historyRoot) { throw 'History destination already exists' }
$notebooks = @(Get-ChildItem -LiteralPath $archiveRoot -File -Filter '*.ipynb')
if ($notebooks.Count -gt 0) { New-Item -ItemType Directory -Path $historyRoot | Out-Null }
foreach ($notebook in $notebooks) {
    Move-Item -LiteralPath $notebook.FullName -Destination (Join-Path $historyRoot $notebook.Name)
}
Remove-Item -LiteralPath $archiveRoot
foreach ($entry in $manifest.files.PSObject.Properties) {
    if ($entry.Value.retention -eq 'notebook history') {
        $entry.Value.file = "runs/$runId/" + [IO.Path]::GetFileName($entry.Value.file)
    }
}
$manifest.state = 'completed; run contains notebook history only; reproduction versions retained separately'
[IO.File]::WriteAllText([IO.Path]::GetFullPath($ManifestPath), ($manifest | ConvertTo-Json -Depth 30), (New-Object Text.UTF8Encoding($false)))
$pointerPath = Join-Path $datasetRoot 'current-run.json'
if (Test-Path -LiteralPath $pointerPath) {
    $pointer = Get-Content -LiteralPath $pointerPath -Raw | ConvertFrom-Json
    if ($pointer.run_id -eq $runId) {
        $relativeNotebook = $pointer.canonical_notebook -replace '^(runs|work)/[^/]+/',''
        $notebookRecord = $manifest.files.PSObject.Properties[$relativeNotebook]
        if ($notebookRecord -and $notebookRecord.Value.retention -eq 'notebook history') {
            $pointer.canonical_notebook = $notebookRecord.Value.file
            [IO.File]::WriteAllText($pointerPath, ($pointer | ConvertTo-Json -Depth 30), (New-Object Text.UTF8Encoding($false)))
        }
    }
}
Write-Output "Archived $runId; notebooks retained at $historyRoot"
