param(
  [ValidateSet('skill','codex','chatgpt','claude','gemini','copilot','cursor','cline','windsurf','opencode','verify','mcp','chat','all')]
  [string]$Mode = 'skill',
  [ValidateSet('user','project')]
  [string]$Scope = $(if ($env:CAPS_SCOPE) { $env:CAPS_SCOPE } else { 'user' })
)

$ErrorActionPreference = 'Stop'
$Repo = if ($env:CAPS_REPO) { $env:CAPS_REPO } else { 'https://github.com/Mutoy-choi/CAPS-Agent-Security.git' }
$RepoWeb = 'https://github.com/Mutoy-choi/CAPS-Agent-Security'
$Ref = if ($env:CAPS_REF) { $env:CAPS_REF } else { 'main' }
$CapsHome = if ($env:CAPS_HOME) { $env:CAPS_HOME } else { Join-Path $HOME '.local/share/caps-unlock-lab' }
$Project = (Get-Location).Path
$Temp = Join-Path ([System.IO.Path]::GetTempPath()) ("caps-" + [guid]::NewGuid())
$Checkout = Join-Path $Temp 'repo'
$CheckoutReady = $false

function Need([string]$Command) {
  if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
    throw "$Command is required for mode '$Mode'"
  }
}

function Ensure-Checkout {
  if ($script:CheckoutReady) { return }
  Need 'git'
  New-Item -ItemType Directory -Force -Path $Temp | Out-Null
  git clone --quiet --depth 1 --branch $Ref $Repo $Checkout
  $script:CheckoutReady = $true
}

function Copy-Skills([string]$Destination) {
  Ensure-Checkout
  New-Item -ItemType Directory -Force -Path $Destination | Out-Null
  foreach ($Skill in @('caps-agent-security','caps-install')) {
    $Target = Join-Path $Destination $Skill
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $Target
    Copy-Item -Recurse (Join-Path $Checkout "skills/$Skill") $Target
  }
  Write-Host "  $Destination"
}

function Install-SharedSkills {
  Write-Host 'Installing CAPS Agent Skills to:'
  if ($Scope -eq 'project') {
    Copy-Skills (Join-Path $Project '.agents/skills')
    Copy-Skills (Join-Path $Project '.claude/skills')
    Copy-Skills (Join-Path $Project '.github/skills')
  } else {
    Copy-Skills (Join-Path $HOME '.agents/skills')
    Copy-Skills (Join-Path $HOME '.claude/skills')
    Copy-Skills (Join-Path $HOME '.copilot/skills')
    Copy-Skills (Join-Path $HOME '.config/opencode/skills')
  }
}

function Install-Codex {
  if ($Scope -eq 'project') { Copy-Skills (Join-Path $Project '.agents/skills') }
  else { Copy-Skills (Join-Path $HOME '.agents/skills') }
  Ensure-Checkout
  New-Item -ItemType Directory -Force -Path $CapsHome | Out-Null
  $Target = Join-Path $CapsHome 'openai-plugin'
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $Target
  Copy-Item -Recurse (Join-Path $Checkout 'plugins/caps-unlock') $Target
  Write-Host "Local ChatGPT/Codex Plugin package: $Target"
}

function Install-Claude {
  Need 'claude'
  try { claude plugin marketplace add Mutoy-choi/CAPS-Agent-Security | Out-Null }
  catch { claude plugin marketplace update caps-labs | Out-Null }
  claude plugin install caps-unlock@caps-labs --scope $Scope
}

function Install-Gemini {
  Need 'gemini'
  try { gemini extensions install $RepoWeb --auto-update }
  catch { gemini extensions update caps-unlock-lab }
}

function Install-Copilot {
  Ensure-Checkout
  if ($Scope -eq 'project') {
    Copy-Skills (Join-Path $Project '.github/skills')
    New-Item -ItemType Directory -Force -Path (Join-Path $Project '.github/agents') | Out-Null
    Copy-Item (Join-Path $Checkout '.github/agents/caps-unlock.md') (Join-Path $Project '.github/agents/caps-unlock.md') -Force
    $Instructions = Join-Path $Project '.github/copilot-instructions.md'
    if (-not (Test-Path $Instructions)) { Copy-Item (Join-Path $Checkout '.github/copilot-instructions.md') $Instructions }
  } else { Copy-Skills (Join-Path $HOME '.copilot/skills') }
}

function Install-ProjectAdapter([string]$Platform) {
  Ensure-Checkout
  switch ($Platform) {
    'cursor' {
      New-Item -ItemType Directory -Force -Path (Join-Path $Project '.cursor/rules') | Out-Null
      Copy-Item (Join-Path $Checkout '.cursor/rules/caps-unlock.mdc') (Join-Path $Project '.cursor/rules/caps-unlock.mdc') -Force
      Copy-Item (Join-Path $Checkout '.cursor/mcp.json.example') (Join-Path $Project '.cursor/mcp.caps.example.json') -Force
    }
    'cline' {
      New-Item -ItemType Directory -Force -Path (Join-Path $Project '.clinerules/workflows') | Out-Null
      Copy-Item (Join-Path $Checkout '.clinerules/caps-unlock.md') (Join-Path $Project '.clinerules/caps-unlock.md') -Force
      Copy-Item (Join-Path $Checkout '.clinerules/workflows/caps-unlock-audit.md') (Join-Path $Project '.clinerules/workflows/caps-unlock-audit.md') -Force
    }
    'windsurf' {
      New-Item -ItemType Directory -Force -Path (Join-Path $Project '.windsurf/rules') | Out-Null
      New-Item -ItemType Directory -Force -Path (Join-Path $Project '.windsurf/workflows') | Out-Null
      Copy-Item (Join-Path $Checkout '.windsurf/rules/caps-unlock.md') (Join-Path $Project '.windsurf/rules/caps-unlock.md') -Force
      Copy-Item (Join-Path $Checkout '.windsurf/workflows/caps-unlock-audit.md') (Join-Path $Project '.windsurf/workflows/caps-unlock-audit.md') -Force
    }
  }
}

function Install-OpenCode {
  if ($Scope -eq 'project') { Copy-Skills (Join-Path $Project '.agents/skills') }
  else { Copy-Skills (Join-Path $HOME '.config/opencode/skills') }
}

function Install-Verify {
  Need 'python'
  Ensure-Checkout
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $CapsHome
  New-Item -ItemType Directory -Force -Path (Split-Path $CapsHome) | Out-Null
  Copy-Item -Recurse $Checkout $CapsHome
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $CapsHome '.git')
  $Venv = Join-Path $CapsHome '.venv'
  python -m venv $Venv
  $Python = Join-Path $Venv 'Scripts/python.exe'
  & $Python -m pip install --upgrade pip
  & $Python -m pip install -e "$(Join-Path $CapsHome 'caps_verify')[gateway,mcp]"
  Write-Host "CAPS Verify installed at $CapsHome"
}

function Prepare-Chat {
  Need 'docker'
  Ensure-Checkout
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $CapsHome
  New-Item -ItemType Directory -Force -Path (Split-Path $CapsHome) | Out-Null
  Copy-Item -Recurse $Checkout $CapsHome
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $CapsHome '.git')
  Write-Host "Run bootstrap.ps1 or bootstrap.sh from $(Join-Path $CapsHome 'caps_app')"
}

try {
  switch ($Mode) {
    'skill' { Install-SharedSkills }
    'codex' { Install-Codex }
    'chatgpt' { Install-Codex }
    'claude' { Install-Claude }
    'gemini' { Install-Gemini }
    'copilot' { Install-Copilot }
    'cursor' { Install-ProjectAdapter 'cursor' }
    'cline' { Install-ProjectAdapter 'cline' }
    'windsurf' { Install-ProjectAdapter 'windsurf' }
    'opencode' { Install-OpenCode }
    'verify' { Install-Verify }
    'mcp' { Install-Verify }
    'chat' { Prepare-Chat }
    'all' {
      Install-SharedSkills
      if (Get-Command claude -ErrorAction SilentlyContinue) { Install-Claude }
      if (Get-Command gemini -ErrorAction SilentlyContinue) { Install-Gemini }
    }
  }
  Write-Host 'CAPS installation complete. Restart the host if the Skill does not appear immediately.'
}
finally {
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $Temp
}
