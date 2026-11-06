[CmdletBinding()]
param(
    [string]$AdminExecutable = 'C:\xampp\mysql\bin\mysqladmin.exe'
)

$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path -Parent $PSScriptRoot
$localDirectory = Join-Path $projectDirectory '.local'
$dataDirectory = Join-Path $localDirectory 'mysql'
if (-not (Test-Path -LiteralPath $dataDirectory -PathType Container)) {
    throw 'No initialized project private database exists at .local/mysql.'
}

$resolvedLocalDirectory = (Resolve-Path -LiteralPath $localDirectory).Path.TrimEnd('\')
$resolvedDataDirectory = (Resolve-Path -LiteralPath $dataDirectory).Path.TrimEnd('\')
$expectedDataDirectory = [IO.Path]::GetFullPath((Join-Path $resolvedLocalDirectory 'mysql')).TrimEnd('\')
$localItem = Get-Item -LiteralPath $localDirectory
$dataItem = Get-Item -LiteralPath $dataDirectory
# OneDrive ReparsePoint attributes alone do not imply a symbolic link/junction.
if ($resolvedDataDirectory -ne $expectedDataDirectory -or
    $localItem.LinkType -in @('SymbolicLink', 'Junction') -or
    $dataItem.LinkType -in @('SymbolicLink', 'Junction')) {
    throw 'Refusing to use a datadir outside the project .local/mysql directory or through a directory link.'
}

$adminConfig = Join-Path $resolvedLocalDirectory 'admin.cnf'
if (-not (Test-Path -LiteralPath $adminConfig -PathType Leaf)) {
    throw 'Private administrator configuration .local/admin.cnf is missing. No shutdown was attempted.'
}
if (-not (Test-Path -LiteralPath $AdminExecutable -PathType Leaf)) {
    throw 'mysqladmin.exe was not found. Supply -AdminExecutable with its installed path.'
}
$resolvedAdminExecutable = (Resolve-Path -LiteralPath $AdminExecutable).Path
$mysqlExecutable = Join-Path (Split-Path -Parent $resolvedAdminExecutable) 'mysql.exe'
if (-not (Test-Path -LiteralPath $mysqlExecutable -PathType Leaf)) {
    throw 'mysql.exe must be beside mysqladmin.exe so the target datadir can be verified safely.'
}

# Read the server's actual datadir before issuing shutdown. Passwords stay in the
# ignored option file and are never passed on the process command line.
$reportedDirectory = & $mysqlExecutable "--defaults-extra-file=$adminConfig" '--protocol=tcp' '--host=127.0.0.1' '--port=3307' '--batch' '--skip-column-names' '--execute=SELECT @@datadir' 2>$null
if ($LASTEXITCODE -ne 0 -or -not $reportedDirectory) {
    throw 'Could not verify the private server on 127.0.0.1:3307. It may already be stopped; no shutdown was attempted.'
}
$reportedDirectory = [IO.Path]::GetFullPath(($reportedDirectory | Select-Object -First 1).Trim()).TrimEnd('\')
if ($reportedDirectory -ne $resolvedDataDirectory) {
    throw 'The server on port 3307 is using a different datadir. Refusing to shut it down.'
}

& $resolvedAdminExecutable "--defaults-extra-file=$adminConfig" '--protocol=tcp' '--host=127.0.0.1' '--port=3307' 'shutdown'
if ($LASTEXITCODE -ne 0) {
    throw 'mysqladmin could not shut down the verified private instance. Check the local server logs.'
}
Write-Output 'The project private database has been shut down cleanly.'
