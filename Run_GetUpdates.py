import os, subprocess

def genUpdateBat_byCheckingAgainstInventory():
	with open("MaterialInventory.txt", 'r') as inputFile, \
			open("Patch.bat", 'w') as outputFile:
		numFiles2Download = 0
		line = inputFile.readline()
		while line:
			filepath, size = line.split("---")
			if os.path.isfile(filepath) and os.path.exists(filepath):
				if (size_Local := os.path.getsize(filepath)) != int(size):
					print("Local size doesn't match inventory:", filepath)
					print("\tFile size to download:", int(size), "Local size:", size_Local)
					numFiles2Download += 1
					writeLine_DownloadfromRepo(filepath, outputFile)
			else:
				print("Can't find in local files:", filepath)
				print("\tFile size to download:", int(size))
				numFiles2Download += 1
				writeLine_DownloadfromRepo(filepath, outputFile)

			line = inputFile.readline()
		print("numFiles2Download:", numFiles2Download)

def writeLine_DownloadfromRepo(filepath, outputFile):
	command = "bitsadmin /transfer job /download /priority normal "
	url = "https://raw.githubusercontent.com/AlarmClockCrusher/HearthstoneSim/master/"
	s = command + url + filepath.replace('\\', '/') + " %cd%\\" + filepath + '\n'
	outputFile.write(s)


"""Down a remote inventory first. Then check and gen UpdateBat. Then execute it"""
def downloadRemoteInventory_CheckAgainstLocal():
	with open('Patch.bat', 'w') as outputFile:
		command = "bitsadmin /transfer job /download /priority normal "
		url = "https://raw.githubusercontent.com/AlarmClockCrusher/HearthstoneSim/master/MaterialInventory.txt"
		outputFile.write(command + url + " %cd%\\MaterialInventory.txt")

	subprocess.Popen(["Patch.bat"], shell=True)
	genUpdateBat_byCheckingAgainstInventory()
	subprocess.Popen(["Patch.bat"], shell=True)
	#os.remove("Patch.bat")


if __name__ == "__main__":
	downloadRemoteInventory_CheckAgainstLocal()