# OpenClaw Studio API Key 配置脚本
# 用于在 Windows PowerShell 中设置 API Key

# Qwen API Key
$QWEN_API_KEY = "sk-fe321dca0bf146ca99df33876ad56bbb"

# 设置环境变量（当前会话）
$env:QWEN_API_KEY = $QWEN_API_KEY

Write-Host "========================================" -ForegroundColor Green
Write-Host "API Key 配置完成" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "QWEN_API_KEY 已设置为当前会话" -ForegroundColor Yellow
Write-Host ""

# 验证配置
$verifyKey = [System.Environment]::GetEnvironmentVariable("QWEN_API_KEY", "Process")
if ($verifyKey) {
    Write-Host "✅ 验证成功: QWEN_API_KEY = $($verifyKey.Substring(0, 20))..." -ForegroundColor Green
} else {
    Write-Host "❌ 验证失败: 未找到 QWEN_API_KEY" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "重要提示" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. 此配置仅在当前 PowerShell 会话中有效" -ForegroundColor Yellow
Write-Host "2. 如果要在新终端中使用，请运行此脚本或手动设置" -ForegroundColor Yellow
Write-Host "3. 设置后需要重启后端服务才能生效" -ForegroundColor Yellow
Write-Host ""
Write-Host "永久设置（可选）:" -ForegroundColor Cyan
Write-Host '  [System.Environment]::SetEnvironmentVariable("QWEN_API_KEY", "sk-fe321dca0bf146ca99df33876ad56bbb", "User")' -ForegroundColor Gray
Write-Host ""
Write-Host "验证配置:" -ForegroundColor Cyan
Write-Host "  python scripts/test_llm_connection.py" -ForegroundColor Gray
Write-Host ""
