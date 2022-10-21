./venv/Scripts/activate.ps1

$HAVE=(Test-Path './dist/mailbox-tk')
if($HAVE -eq "True")  {
    Remove-Item -Recurse -Force './dist/mailbox-tk'
}

$HAVE=(Test-Path './dist/sender-tk')
if($HAVE -eq "True")  {
    Remove-Item -Recurse -Force './dist/sender-tk'
}

$HAVE=(Test-Path './dist/mailbox-cli.exe')
if($HAVE -eq "True")  {
    Remove-Item -Force './dist/mailbox-cli.exe'
}

$HAVE=(Test-Path './dist/sender-cli.exe')
if($HAVE -eq "True")  {
    Remove-Item -Force './dist/sender-cli.exe'
}

$HAVE=(Test-Path './dist/mailbox-tk.zip')
if($HAVE -eq "True")  {
    Remove-Item -Force './dist/mailbox-tk.zip'
}

$HAVE=(Test-Path './dist/sender-tk.zip')
if($HAVE -eq "True")  {
    Remove-Item -Force './dist/sender-tk.zip'
}


pyinstaller -F -i "./static/HuanMail.ico" "./sender-cli.py"
pyinstaller -F -i "./static/HuanMail.ico" "./mailbox-cli.py"
pyinstaller -w -i "./static/HuanMail.ico" "./sender-tk.py"
pyinstaller -w -i "./static/HuanMail.ico" "./mailbox-tk.py"

mkdir "./dist/mailbox-tk/static"
mkdir "./dist/sender-tk/static"

copy-item "./static/HuanMail.ico" -Destination "./dist/mailbox-tk/static"
copy-item "./static/HuanMail.ico" -Destination "./dist/sender-tk/static"

Compress-Archive -Path "./dist/mailbox-tk" -DestinationPath "./dist/mailbox-tk.zip"
Compress-Archive -Path "./dist/sender-tk" -DestinationPath "./dist/sender-tk.zip"

Write-Output "SUCCESS!"
