$port = 8000

Write-Host "Checking port $port..."

$connections = netstat -ano | findstr ":$port"

if ($connections) {
    Write-Host "Found processes using port ${port}:"
    Write-Host $connections

    $pids = $connections |
        ForEach-Object {
            ($_ -split "\s+")[-1]
        } |
        Sort-Object -Unique

    foreach ($processId in $pids) {
        if ($processId -match "^\d+$") {
            Write-Host "Killing process PID: $processId"
            taskkill /PID $processId /F
        }
    }
} else {
    Write-Host "Port $port is free."
}

Write-Host "Starting FastAPI server..."
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload