Set WShell = CreateObject("WScript.Shell")
' Start Flask server
WShell.Run "C:\Users\22602\html-share\start_flask.bat", 0, False
WScript.Sleep 5000
' Start Cloudflare Tunnel
WShell.Run "C:\Users\22602\html-share\start_tunnel.bat", 0, False
