$htmlPath = (Resolve-Path "report.html").Path
$pdfPath = Join-Path (Get-Location).Path "report.pdf"

$edgePaths = @(
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "${env:LOCALAPPDATA}\Microsoft\Edge\Application\msedge.exe"
)

$browser = $null
foreach ($p in $edgePaths) {
    if (Test-Path $p) { $browser = $p; break }
}

if ($browser) {
    Write-Host "Using: $browser"
    Start-Process -FilePath $browser -ArgumentList "--headless","--disable-gpu","--print-to-pdf=$pdfPath","--no-pdf-header-footer",$htmlPath -Wait -NoNewWindow
    if (Test-Path $pdfPath) {
        $size = [math]::Round((Get-Item $pdfPath).Length / 1KB)
        Write-Host "PDF: report.pdf ($size KB)"
    }
} else {
    Write-Host "No browser found. Open report.html in browser and Ctrl+P to save as PDF."
}
