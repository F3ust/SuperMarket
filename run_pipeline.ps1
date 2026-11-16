param(
    [ValidateSet('train','score')][string]$Mode = 'train',
    [string]$AsOf = '',
    [string]$Config = '',
    [string]$Python = 'C:\Users\pc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',
    [switch]$Force
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath $Python)) { throw "Python interpreter not found: $Python" }
$moduleName = if ($Mode -eq 'train') { 'retail_pipeline.run' } else { 'retail_pipeline.score' }
$pipelineArgs = @('-m', $moduleName)
if ($Config) { $pipelineArgs += @('--config', $Config) }
if ($AsOf) {
    if ($Mode -ne 'score') { throw 'For training, set analysis_end in a separate config file.' }
    $pipelineArgs += @('--as-of', $AsOf)
}
if ($Force -and $Mode -eq 'train') { $pipelineArgs += '--force' }
& $Python @pipelineArgs
exit $LASTEXITCODE
