[CmdletBinding()]
param(
    [string]$ServerExecutable = 'C:\xampp\mysql\bin\mysqld.exe'
)

# This helper starts only the private datadir already initialized for this project.
# It never initializes, copies, repairs, deletes, or changes XAMPP's normal data.
$ErrorActionPreference = 'Stop'
$projectDirectory = Split-Path -Parent $PSScriptRoot
$localDirectory = Join-Path $projectDirectory '.local'
$dataDirectory = Join-Path $localDirectory 'mysql'

if (-not (Test-Path -LiteralPath $dataDirectory -PathType Container)) {
    throw 'The private .local/mysql instance has not been initialized on this machine. Use the normal README database setup instead.'
}

$resolvedLocalDirectory = (Resolve-Path -LiteralPath $localDirectory).Path.TrimEnd('\')
$resolvedDataDirectory = (Resolve-Path -LiteralPath $dataDirectory).Path.TrimEnd('\')
$expectedDataDirectory = [IO.Path]::GetFullPath((Join-Path $resolvedLocalDirectory 'mysql')).TrimEnd('\')
$localItem = Get-Item -LiteralPath $localDirectory
$dataItem = Get-Item -LiteralPath $dataDirectory
# OneDrive folders can have ReparsePoint without being links. Reject actual
# directory links, while allowing cloud placeholder attributes on normal folders.
if ($resolvedDataDirectory -ne $expectedDataDirectory -or
    $localItem.LinkType -in @('SymbolicLink', 'Junction') -or
    $dataItem.LinkType -in @('SymbolicLink', 'Junction')) {
    throw 'Refusing to use a datadir outside the project .local/mysql directory or through a directory link.'
}
if (-not (Test-Path -LiteralPath (Join-Path $resolvedDataDirectory 'mysql') -PathType Container)) {
    throw 'The private datadir is missing its initialized mysql system database.'
}
if (-not (Test-Path -LiteralPath $ServerExecutable -PathType Leaf)) {
    throw 'mysqld.exe was not found. Supply -ServerExecutable with the MariaDB executable used to initialize this private instance.'
}

$resolvedServerExecutable = (Resolve-Path -LiteralPath $ServerExecutable).Path
$binaryDirectory = Split-Path -Parent $resolvedServerExecutable
$baseDirectory = Split-Path -Parent $binaryDirectory
$mysqlExecutable = Join-Path $binaryDirectory 'mysql.exe'
$adminConfig = Join-Path $resolvedLocalDirectory 'admin.cnf'

# If an instance already answers on this port, verify its datadir before reusing it.
$portInUse = $false
$connectionProbe = New-Object System.Net.Sockets.TcpClient
try {
    $connectionProbe.Connect('127.0.0.1', 3307)
    $portInUse = $true
} catch {
    $portInUse = $false
} finally {
    $connectionProbe.Dispose()
}
if ($portInUse) {
    if ((Test-Path -LiteralPath $adminConfig -PathType Leaf) -and
        (Test-Path -LiteralPath $mysqlExecutable -PathType Leaf)) {
        $reportedDirectory = & $mysqlExecutable "--defaults-extra-file=$adminConfig" '--protocol=tcp' '--host=127.0.0.1' '--port=3307' '--batch' '--skip-column-names' '--execute=SELECT @@datadir' 2>$null
        if ($LASTEXITCODE -eq 0 -and $reportedDirectory) {
            $reportedDirectory = [IO.Path]::GetFullPath(($reportedDirectory | Select-Object -First 1).Trim()).TrimEnd('\')
            if ($reportedDirectory -eq $resolvedDataDirectory) {
                Write-Output 'The project private database is already running on 127.0.0.1:3307.'
                return
            }
        }
    }
    throw 'Port 3307 is already in use and could not be verified as this project private database. No new process was started.'
}

$stdoutLog = Join-Path $resolvedLocalDirectory 'mysql-stdout.log'
$stderrLog = Join-Path $resolvedLocalDirectory 'mysql-stderr.log'
$serverErrorLog = Join-Path $resolvedLocalDirectory 'mysql-error.log'
$privatePidFile = Join-Path $resolvedDataDirectory 'mathmyst-private.pid'
$serverArguments = @(
    '--no-defaults',
    ('--basedir="{0}"' -f $baseDirectory),
    ('--datadir="{0}"' -f $resolvedDataDirectory),
    '--port=3307',
    '--bind-address=127.0.0.1',
    ('--pid-file="{0}"' -f $privatePidFile),
    ('--log-error="{0}"' -f $serverErrorLog),
    '--console'
)

$databaseProcess = Start-Process -FilePath $resolvedServerExecutable -ArgumentList $serverArguments -WorkingDirectory $projectDirectory -WindowStyle Hidden -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -PassThru
for ($attemptNumber = 0; $attemptNumber -lt 20; $attemptNumber++) {
    Start-Sleep -Milliseconds 500
    $databaseProcess.Refresh()
    if ($databaseProcess.HasExited) {
        throw 'The private database exited during startup. Inspect .local/mysql-error.log and .local/mysql-stderr.log.'
    }
    $connectionProbe = New-Object System.Net.Sockets.TcpClient
    try {
        $connectionProbe.Connect('127.0.0.1', 3307)
        Write-Output "Private database started on 127.0.0.1:3307 (process $($databaseProcess.Id))."
        return
    } catch {
        # The process may need another moment to finish InnoDB startup.
    } finally {
        $connectionProbe.Dispose()
    }
}
throw 'The database process was launched but did not accept connections within 10 seconds. Inspect the .local log files before trying again.'
