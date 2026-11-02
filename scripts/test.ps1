$ErrorActionPreference = "Stop"

if (-not (Test-Path ".\token.txt")) {
    throw "token.txt not found. First run: python .\scripts\setup_dev.py"
}

$token = (Get-Content ".\token.txt" -Raw).Trim()

Write-Host "`n1) Request without a token (expected: HTTP 401)"
curl.exe -i "http://localhost/headers"

Write-Host "`n2) Request with an invalid token (expected: HTTP 401)"
curl.exe -i -H "Authorization: Bearer invalid-token" "http://localhost/headers"

Write-Host "`n3) Request with the generated valid token (expected: HTTP 200)"
curl.exe -i -H "Authorization: Bearer $token" "http://localhost/headers"

Write-Host "`n4) Backend should NOT be published on host port 8081."
Test-NetConnection -ComputerName localhost -Port 8081
