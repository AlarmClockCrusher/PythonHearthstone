import os

def findStartandEndIndex_ofWord(s, word):
	length = len(word)
	for index in range(len(s) - length):
		if s[index:index + length] == word:
			break
	return index, index+length-1

def findStartIndex_VarattheEnd(s):
	length = len(s)
	i = next((i for i in range(length) if s[:length] and all(c.isnumeric() or c.isalpha() or c == '_'
															for c in s[i:length])), -1)
	return i

#最终效果如下。用于对调var.func(xxxxx, creator=name-----，成为name.func(var, xxxxx-----，
#Orig:    self.keeper.func(self.keeper, func=lambda minion: minion.buffDebuff(2, 1, creator=self.keeper),
#Split    self.keeper.func(self.keeper, func=lambda minion:  | minion | .buffDebuff( | 2, 1 | , creator=self.keeper | ),
#New      self.keeper.func(self.keeper, func=lambda minion: self.keeper.buffDebuff(minion, 2, 1),
def invertInitatorandCreator(s, funcName, creatorString):
	before, after = s.split(funcName)
	index0_Var = findStartIndex_VarattheEnd(before)
	if index0_Var < 0: return ''
	start, initiator = before[:index0_Var], before[index0_Var:]
	after1, after2 = after.split(creatorString)
	creator = creatorString.replace(", creator=", '')
	newLine = start + creator + funcName + initiator + ', ' + after1 + after2

	#print("Orig:   ", s, end="")
	#print("Split   ", start, "|", initiator, "|", funcName, "|", after1, "|", creatorString, "|", after2)
	print("New     ", newLine)
	return newLine


for file in os.listdir('.'):
	if file.startswith("HS_") and file.endswith('.py'):
		print(file)
		with open(file, 'r', encoding="utf-8") as inputFile, \
			open("Backup\\"+file, 'a', encoding='utf-8') as outputFile:
			line = inputFile.readline()
			while line:
				if ".buffDebuff(" in line:
					if "creator=self.keeper" in line: creatorString = ", creator=self.keeper"
					elif "creator=self" in line: creatorString = ", creator=self"
					else: creatorString = ''
					print("Orig:   ", line, end="")
					if creatorString and (s := invertInitatorandCreator(line, funcName=".buffDebuff(",
																			creatorString=creatorString)):
						outputFile.write(s)
					else:
						print("FAILED!!!")
						outputFile.write(line)
				else: outputFile.write(line)
				line = inputFile.readline()