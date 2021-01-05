@Echo OFF

If Not Exist %USERPROFILE%\anaconda3\Scripts\activate.bat (
	Call :downloadFile "https://repo.anaconda.com/archive/" "Anaconda3-2020.11-Windows-x86_64.exe"
	Start /WAIT %temp%\Anaconda3-2020.11-Windows-x86_64.exe
)

Where nvcc
If %ERRORLEVEL%==0 Goto server

Echo CUDA technology is strongly recommended to run this program. Below is your GPU name, please check if it's supported by CUDA technology to download CUDA installer
Echo https://developer.nvidia.com/cuda-gpus
Call wmic Path win32_VideoController get name
:while
Set /p id="[Y/n]: "
If "%id%"=="Y" Or "%id%"=="y" Goto cudainstall
If "%id%" NEQ "n" Goto while

:cudainstall
Call :downloadFile "https://developer.download.nvidia.com/compute/cuda/11.2.0/network_installers/" "cuda_11.2.0_win10_network.exe"
Start /WAIT %temp%\cuda_11.2.0_win10_network.exe

:server
Call %USERPROFILE%\anaconda3\Scripts\activate.bat
If Not Exist %USERPROFILE%\anaconda3\envs\mtgenv (
	Call conda env create -f environment.yml
)

Call conda activate mtgenv
Call uvicorn mtg_django.asgi:application --reload --debug --ws websockets
start "" http://localhost:8000/

Goto:eof

:downloadFile <downloadaddress> <downloadfile>
set vbs="%temp%\_.vbs"
>>%vbs% Echo strFileURL = %1 + %2
>>%vbs% Echo strHDLocation = "%temp%\"
>>%vbs% Echo Set objXMLHTTP = CreateObject("MSXML2.XMLHTTP")
>>%vbs% Echo objXMLHTTP.open "GET", strFileURL, false
>>%vbs% Echo objXMLHTTP.send() 
>>%vbs% Echo If objXMLHTTP.Status = 200 Then
>>%vbs% Echo Set objADOStream = CreateObject("ADODB.Stream")
>>%vbs% Echo objADOStream.Open
>>%vbs% Echo objADOStream.Type = 1 'adTypeBinary
>>%vbs% Echo objADOStream.Write objXMLHTTP.ResponseBody
>>%vbs% Echo objADOStream.Position = 0    'Set the stream position to the start
>>%vbs% Echo Set objFSO = CreateObject("Scripting.FileSystemObject")	
>>%vbs% Echo If Not objFSO.Fileexists(strHDLocation + %2) Then
>>%vbs% Echo Set objFSO = Nothing
>>%vbs% Echo objADOStream.SaveToFile(strHDLocation + %2)
>>%vbs% Echo objADOStream.Close
>>%vbs% Echo Set objADOStream = Nothing
>>%vbs% Echo End if
>>%vbs% Echo End if
>>%vbs% Echo Set objXMLHTTP = Nothing
cscript //nologo %vbs%
if exist %vbs% Del /f /q %vbs%
Goto:eof

:UnZipFile <ExtractTo> <newzipfile>
set vbs="%temp%\_.vbs"
if exist %vbs% Del /f /q %vbs%
>>%vbs% Echo Set fso = CreateObject("Scripting.FileSystemObject")
>>%vbs% Echo If NOT fso.FolderExists(%1) Then
>>%vbs% Echo fso.CreateFolder(%1)
>>%vbs% Echo End If
>>%vbs% Echo set objShell = CreateObject("Shell.Application")
>>%vbs% Echo set FilesInZip=objShell.NameSpace(%2).items
>>%vbs% Echo objShell.NameSpace(%1).CopyHere(FilesInZip)
>>%vbs% Echo Set fso = Nothing
>>%vbs% Echo Set objShell = Nothing
cscript //nologo %vbs%
If Exist %vbs% Del /f /q %vbs%
Goto:eof

Pause