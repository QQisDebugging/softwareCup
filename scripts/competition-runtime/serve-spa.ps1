param(
    [string]$Root = (Join-Path $PSScriptRoot "frontend"),
    [int]$Port = 5173
)

$ErrorActionPreference = "Stop"

function Get-ContentType {
    param([string]$Path)
    switch ([System.IO.Path]::GetExtension($Path).ToLowerInvariant()) {
        ".html" { "text/html; charset=utf-8"; break }
        ".js" { "text/javascript; charset=utf-8"; break }
        ".mjs" { "text/javascript; charset=utf-8"; break }
        ".css" { "text/css; charset=utf-8"; break }
        ".json" { "application/json; charset=utf-8"; break }
        ".png" { "image/png"; break }
        ".jpg" { "image/jpeg"; break }
        ".jpeg" { "image/jpeg"; break }
        ".svg" { "image/svg+xml"; break }
        ".ico" { "image/x-icon"; break }
        ".woff" { "font/woff"; break }
        ".woff2" { "font/woff2"; break }
        default { "application/octet-stream" }
    }
}

$rootPath = [System.IO.Path]::GetFullPath($Root)
$indexPath = Join-Path $rootPath "index.html"
if (-not (Test-Path -LiteralPath $indexPath)) {
    throw "Cannot find frontend index.html at $indexPath"
}

$listener = [System.Net.HttpListener]::new()
$prefix = "http://localhost:$Port/"
$listener.Prefixes.Add($prefix)
$listener.Start()
Write-Host "Frontend SPA server listening at $prefix"
Write-Host "Serving files from $rootPath"

try {
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        try {
            $requestPath = [Uri]::UnescapeDataString($context.Request.Url.AbsolutePath.TrimStart("/"))
            if ([string]::IsNullOrWhiteSpace($requestPath)) {
                $filePath = $indexPath
            } else {
                $candidate = [System.IO.Path]::GetFullPath((Join-Path $rootPath ($requestPath -replace "/", [System.IO.Path]::DirectorySeparatorChar)))
                if ($candidate.StartsWith($rootPath, [System.StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $candidate -PathType Leaf)) {
                    $filePath = $candidate
                } else {
                    $filePath = $indexPath
                }
            }

            $bytes = [System.IO.File]::ReadAllBytes($filePath)
            $context.Response.StatusCode = 200
            $context.Response.ContentType = Get-ContentType $filePath
            $context.Response.ContentLength64 = $bytes.Length
            $context.Response.OutputStream.Write($bytes, 0, $bytes.Length)
        } catch {
            $message = [System.Text.Encoding]::UTF8.GetBytes("Static server error: $($_.Exception.Message)")
            $context.Response.StatusCode = 500
            $context.Response.ContentType = "text/plain; charset=utf-8"
            $context.Response.ContentLength64 = $message.Length
            $context.Response.OutputStream.Write($message, 0, $message.Length)
        } finally {
            $context.Response.OutputStream.Close()
        }
    }
} finally {
    $listener.Close()
}
