param(
    [switch]$Render,
    [string]$Python = 'C:\Users\pc\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath $Python)) { throw "Python interpreter not found: $Python" }
& $Python -m retail_pipeline.run
if ($LASTEXITCODE -ne 0) { throw 'Core pipeline failed; report generation stopped.' }
& $Python research/deep_analysis.py
if ($LASTEXITCODE -ne 0) { throw 'Deep analysis failed; report generation stopped.' }
& $Python research/build_word_report.py
if ($LASTEXITCODE -ne 0) { throw 'Word generation stopped. Inspect source-version or content-review requirements.' }
if ($Render) {
    & $Python research/render_word_native.py outputs/word_report/Bao_cao_chuyen_sau_chuoi_sieu_thi.docx --output_dir outputs/word_report/render --emit_pdf
    if ($LASTEXITCODE -ne 0) { throw 'Word render verification failed.' }
}
Write-Output 'Word report generated. Inspect rendered pages before issuing a changed edition.'
