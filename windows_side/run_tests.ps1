Write-Output "Triggering test run in WSL controller..."

Invoke-RestMethod http://localhost:5000/health
Invoke-RestMethod http://localhost:5000/metrics
Invoke-RestMethod http://localhost:5001/redfish/v1/