param(
    [Parameter(Mandatory = $true)]
    [string] $StackName
)

$ErrorActionPreference = "Stop"

function Invoke-Aws {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]] $AwsArgs)
    $output = & aws --no-cli-pager @AwsArgs
    if ($LASTEXITCODE -ne 0) {
        throw "aws $($AwsArgs -join ' ') に失敗しました。"
    }
    return $output
}

$json = Invoke-Aws cloudformation describe-stacks --stack-name $StackName --output json | Out-String
$stack = $json | ConvertFrom-Json
$outputs = @{}
foreach ($output in @($stack.Stacks[0].Outputs)) {
    if ($null -eq $output) { continue }
    $outputs[$output.OutputKey] = $output.OutputValue
}

$apiUrl = $outputs["ApiUrl"]
$bucket = $outputs["FrontendBucketName"]
$distributionId = $outputs["FrontendDistributionId"]
$frontendUrl = $outputs["FrontendUrl"]
if (-not $apiUrl -or -not $bucket -or -not $distributionId) {
    throw "スタック $StackName に ApiUrl、FrontendBucketName、FrontendDistributionId がありません。"
}

$frontend = Join-Path (Split-Path -Parent $PSScriptRoot) "frontend"
$previousApiUrl = $env:VITE_API_URL
Push-Location $frontend
try {
    $env:VITE_API_URL = $apiUrl.TrimEnd("/")
    npm ci
    if ($LASTEXITCODE -ne 0) {
        throw "npm ci に失敗しました。"
    }
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "npm run build に失敗しました。"
    }
}
finally {
    if ($null -eq $previousApiUrl) {
        Remove-Item Env:VITE_API_URL -ErrorAction SilentlyContinue
    }
    else {
        $env:VITE_API_URL = $previousApiUrl
    }
    Pop-Location
}

Invoke-Aws s3 sync (Join-Path $frontend "dist") "s3://$bucket" --delete | Out-Host
Invoke-Aws cloudfront create-invalidation --distribution-id $distributionId --paths "/*" | Out-Host
Write-Host "配信先: $frontendUrl"
