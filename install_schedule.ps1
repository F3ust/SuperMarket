param(
    [string]$TaskName = 'SieuThi-Retail-Analytics',
    [string]$DailyTime = '06:00',
    [ValidateSet('train','score')][string]$Mode = 'train'
)
$ErrorActionPreference = 'Stop'
if ((Get-TimeZone).Id -ne 'SE Asia Standard Time') {
    throw 'Set Windows time zone to Asia/Saigon (SE Asia Standard Time) or adapt the trigger explicitly before installing.'
}
$runnerPath = Join-Path $PSScriptRoot 'run_pipeline.ps1'
if (-not (Test-Path -LiteralPath $runnerPath)) { throw 'Missing pipeline runner.' }
$taskArguments = '-NoProfile -NonInteractive -WindowStyle Hidden -File "' + $runnerPath + '" -Mode ' + $Mode
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $taskArguments -WorkingDirectory $PSScriptRoot
$trigger = New-ScheduledTaskTrigger -Daily -At ([datetime]::ParseExact($DailyTime, 'HH:mm', $null))
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Hours 2)
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) { throw 'Task already exists. Inspect it before replacing.' }
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description 'Local retail pipeline. Historical inputs remain static until replaced; unchanged full runs skip.'
