Set-Location -Path (Join-Path $PSScriptRoot "..");

Write-Output "(Press Any Key to Start)";
while ($true) { 
    [System.Console]::ReadKey($true); Clear-Host; python.exe src/main_gui.py;
    Write-Output "Finished (Press Any Key to Start)";
}