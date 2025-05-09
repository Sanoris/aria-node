@echo off
setlocal enabledelayedexpansion

REM === CONFIGURATION ===
set SYNC_PEER=127.0.0.1
set PORT=50051
set /p COUNT="Enter the number of nodes to deploy: "
echo  Generating .env files...

for /L %%I in (1,1,%COUNT%) do (
    set ID=%%I
    echo NODE_ID=aria-node-!ID! > .env.!ID!
    echo SYNC_PEER=%SYNC_PEER% >> .env.!ID!
    echo PORT=50051 >> .env.!ID!
    echo  Created .env.!ID!
)

REM Optional: Mount BitNet model directory if available
REM docker build -t aria-node-node:latest .
REM docker build -f Dockerfile_LLM -t aria-node-full .
REM === Launch dashboard node ===
docker run -d ^
    --name aria-dashboard ^
    -e NODE_ID=aria-dashboard ^
    -e SYNC_PEER=127.0.0.1 ^
    -v "%cd%\aria_dashboard:/app/aria_dashboard" ^
    -v "%cd%\plugins:/app/plugins" ^
    -v "%cd%\crypto\keys:/app/crypto/keys" ^
    -v "%cd%\crypto\keys\ARIA_AES_KEY.txt:/app/crypto/keys/ARIA_AES_KEY.txt" ^
    -v "%cd%\aria_proxy:/app/aria_proxy" ^
    -v "%cd%\nginx:/etc/nginx/conf.d" ^
    -v "%cd%\BitNet:/app/BitNet" ^
    -p 8001:8001 ^
    -it ^
    aria-node-full:latest



REM === Launch swarm nodes ===
for /L %%I in (1,1,%COUNT%) do (
    set ID=%%I
    set NODE_ID=aria-node-!ID!
    set SYNC_PEER=%SYNC_PEER%
    set PORT=50051
    echo -------------------------------------
    echo  Using config: !NODE_ID!

    if not exist "crypto\keys\!NODE_ID!" (
        mkdir "crypto\keys\!NODE_ID!"
        echo  Created key folder: crypto\keys\!NODE_ID!
    )

    docker run -d ^
        --name !NODE_ID! ^
        -e NODE_ID=!NODE_ID! ^
        -e SYNC_PEER=!SYNC_PEER! ^
        -v "%cd%\plugins:/app/plugins" ^
        -v "%cd%\crypto\keys\!NODE_ID!:/app/crypto/keys" ^
        -v "%cd%\aria_dashboard:/app/aria_dashboard" ^
        -v "%cd%\plugins:/app/plugins" ^
        -v "%cd%\crypto\keys\ARIA_AES_KEY.txt:/app/crypto/keys/ARIA_AES_KEY.txt" ^
        -v "%cd%\aria_proxy:/app/aria_proxy" ^
        -v "%cd%\nginx:/etc/nginx/conf.d" ^
        -v "%cd%\BitNet:/app/BitNet" ^
        aria-node-full:latest

    echo  Launched !NODE_ID!
)

echo -------------------------------------
echo  Aria swarm deployed with self-routing proxy plugin.
endlocal
pause