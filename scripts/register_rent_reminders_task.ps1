$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$managePath = Join-Path $projectRoot 'manage.py'
$pythonCandidates = @(
    (Join-Path $projectRoot '.venv\Scripts\python.exe'),
    (Join-Path $projectRoot 'venv\Scripts\python.exe')
)
$pythonPath = $pythonCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if (-not $pythonPath) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw 'Python est introuvable. Activez votre environnement Python ou ajoutez Python au PATH.'
    }
    $pythonPath = $pythonCommand.Source
}

$smtpStatus = & $pythonPath $managePath shell -c "from django.conf import settings; print('SMTP_CONFIGURED' if settings.EMAIL_HOST else 'SMTP_MISSING')"
if ($LASTEXITCODE -ne 0) {
    throw 'Impossible de vérifier la configuration e-mail Django.'
}
if ($smtpStatus -notcontains 'SMTP_CONFIGURED') {
    throw 'Configurez EMAIL_HOST dans .env avant de programmer les rappels, sinon les e-mails ne seront pas remis aux locataires.'
}

$taskName = 'Imo-Rappels-Loyers'
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument ('"{0}" process_rent_reminders' -f $managePath) -WorkingDirectory $projectRoot
$trigger = New-ScheduledTaskTrigger -Daily -At '9:00AM'
$principal = New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Description 'Met à jour les loyers en retard et envoie les rappels Imo.'
Register-ScheduledTask -TaskName $taskName -InputObject $task -Force | Out-Null
Write-Host "La tâche $taskName est programmée chaque jour à 09:00 pour l'utilisateur connecté."
