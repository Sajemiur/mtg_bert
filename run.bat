@ECHO OFF

IF NOT EXIST %USERPROFILE%\anaconda3\Scripts\activate.bat (
	START /WAIT cscript //nologo downloader.vbs "https://repo.anaconda.com/archive/" "Anaconda3-2020.11-Windows-x86_64.exe"
	START /WAIT installers\Anaconda3-2020.11-Windows-x86_64.exe
)

WHERE nvcc
IF %ERRORLEVEL%==0 goto conda

ECHO CUDA technology is strongly recommended to run this program. Below is your GPU name, please check if it's supported by CUDA technology to download CUDA installer
ECHO https://developer.nvidia.com/cuda-gpus
call wmic path win32_VideoController get name
:while
set /p id="[Y/n]: "
IF "%id%"=="Y" OR "%id%"=="y" goto cudainstall
IF "%id%" NEQ "n" goto while

:cudainstall
START /WAIT cscript //nologo downloader.vbs "https://developer.download.nvidia.com/compute/cuda/11.2.0/network_installers/" "cuda_11.2.0_win10_network.exe"
START /WAIT installers\cuda_11.2.0_win10_network.exe

:conda
call %USERPROFILE%\anaconda3\Scripts\activate.bat
IF NOT EXIST %USERPROFILE%\anaconda3\envs\mtgenv (
	call conda env create -f environment.yml
)

call conda activate mtgenv
call uvicorn mtg_django.asgi:application --reload --debug --ws websockets

pause