strFileURL = WScript.Arguments(0) + WScript.Arguments(1)
strHDLocation = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) + "\installers\"

Set objXMLHTTP = CreateObject("MSXML2.XMLHTTP")

objXMLHTTP.open "GET", strFileURL, false
objXMLHTTP.send()

If objXMLHTTP.Status = 200 Then
	Set objADOStream = CreateObject("ADODB.Stream")
	objADOStream.Open
	objADOStream.Type = 1 'adTypeBinary

	objADOStream.Write objXMLHTTP.ResponseBody
	objADOStream.Position = 0    'Set the stream position to the start

	Set objFSO = CreateObject("Scripting.FileSystemObject")
	
	If Not objFSO.Fileexists(strHDLocation + WScript.Arguments(1)) Then
		If Not objFSO.Fileexists(strHDLocation) Then objFSO.CreateFolder(strHDLocation)
		Set objFSO = Nothing

		objADOStream.SaveToFile (strHDLocation + WScript.Arguments(1))
		objADOStream.Close
		Set objADOStream = Nothing
	End if
End if

Set objXMLHTTP = Nothing