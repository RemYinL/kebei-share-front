param([string]$Action = "status")

$FlaskScript = "C:\Users\22602\html-share\start_flask.bat"
$TunnelScript = "C:\Users\22602\html-share\start_tunnel.bat"
$Python = "C:\Users\22602\AppData\Local\Programs\Python\Python313\python.exe"
$Cloudflared = "C:\Users\22602\bin\cloudflared.exe"
$TunnelID = "f7bf0b16-a511-45a9-963d-347c57b29cb7"
$FlaskPort = 5000

function Get-FlaskRunning {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$FlaskPort/login" -TimeoutSec 3 -UseBasicParsing
        return $true
    } catch { return $false }
}

function Get-TunnelRunning {
    $p = Get-Process -Name "cloudflared*" -ErrorAction SilentlyContinue
    return ($p -ne $null)
}

switch ($Action) {
    "start" {
        Write-Host "Starting Flask..." -ForegroundColor Cyan
        if (-not (Get-FlaskRunning)) {
            Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $FlaskScript -WindowStyle Hidden
            Write-Host "  Flask starting..." -ForegroundColor Green
        } else {
            Write-Host "  Flask already running" -ForegroundColor Yellow
        }
        Start-Sleep 3
        Write-Host "Starting Tunnel..." -ForegroundColor Cyan
        if (-not (Get-TunnelRunning)) {
            Start-Process -FilePath "cmd.exe" -ArgumentList "/c", $TunnelScript -WindowStyle Hidden
            Write-Host "  Tunnel starting..." -ForegroundColor Green
        } else {
            Write-Host "  Tunnel already running" -ForegroundColor Yellow
        }
    }
    "stop" {
        Write-Host "Stopping services..." -ForegroundColor Cyan
        Get-Process -Name "cloudflared*" -ErrorAction SilentlyContinue | Stop-Process -Force
        Write-Host "  Tunnel stopped" -ForegroundColor Green
        $fport = $FlaskPort
        $conn = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners()
        $flaskListeners = $conn | Where-Object { $_.Port -eq $fport -and $_.Address -eq [System.Net.IPAddress]::Any }
        if ($flaskListeners) {
            # Can't stop by port, need to find PID
            $pid = (Get-NetTCPConnection -LocalPort $fport -ErrorAction SilentlyContinue).OwningProcess
            if ($pid) { Stop-Process -Id $pid -Force }
        }
        Write-Host "  Flask stopped" -ForegroundColor Green
    }
    "restart" {
        & $PSCommandPath -Action stop
        Start-Sleep 2
        & $PSCommandPath -Action start
    }
    default {
        Write-Host "=== 科贝智色 服务状态 ===" -ForegroundColor Cyan
        $f = Get-FlaskRunning
        if ($f) {
            Write-Host "[Flask]    :5000  RUNNING" -ForegroundColor Green
        } else {
            Write-Host "[Flask]    :5000  STOPPED" -ForegroundColor Red
        }
        $t = Get-TunnelRunning
        if ($t) {
            Write-Host "[Tunnel]   隧道    RUNNING" -ForegroundColor Green
            & $Cloudflared tunnel info $TunnelID 2>&1 | Select-String "CONNECTOR"
        } else {
            Write-Host "[Tunnel]   隧道    STOPPED" -ForegroundColor Red
        }
    }
}
