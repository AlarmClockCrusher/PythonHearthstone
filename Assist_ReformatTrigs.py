import os
from DB_CardPools import cardPool_All


def allTabsandReturnsinLine(s):
	return all(c == "\t" or c == "\n" for c in s)

def isaLineofComment(line):
	return line.strip('\t').startswith('#')

def returnStrListsofaDoc(inputFile):
	lines = []
	line = inputFile.readline()
	while line:
		lines.append(line)
		line = inputFile.readline()
	return lines


def removeTripleReturnsinFiles(prefix="HS_", origFilePath='.', newFilePath="Backup"):
	for file in os.listdir('.'):
		if file.startswith("HS_") and file.endswith('.py'):
			print("\n\nPROCESSING FILE", file)
			with open(origFilePath+"\\"+file, 'r', encoding="utf-8") as input, \
					open(newFilePath+"\\"+file, 'w', encoding="utf-8") as output:
				lines = returnStrListsofaDoc(input)
				for i in reversed(range(len(lines))):
					if allTabsandReturnsinLine(lines[i]) \
						and allTabsandReturnsinLine(lines[i-1]) \
							and allTabsandReturnsinLine(lines[i-2]):
						print("Found one at line number: ", i)
						lines.pop(i)

				for line in lines: output.write(line)


#for file in os.listdir('.'):
#	if file.startswith("HS_") and file.endswith('.py'):
#		print(file)
#		with open(file, 'r', encoding="utf-8") as input, \
#				open("Backup\\"+file, 'w', encoding="utf-8") as output:
#			lines = returnStrListsofaDoc(input)
#
#			for i in reversed(range(len(lines))):
#				if "self.trigsBoard = [" in lines[i]:
#					print("Line number", i, lines[i], end="")
#					lines[i] = "\ttrigBoard = " + lines[i].split("= [")[1].split("(self")[0]
#					if "__init__" in lines[i-1]: lines.pop(i-1)
#					if "__init__" in lines[i-2]: lines.pop(i-2)
#					print(lines[i])
#				if "self.trigsHand = [" in lines[i]:
#					print("Line number", i, lines[i], end="")
#					lines[i] = "\ttrigHand = " + lines[i].split("= [")[1].split("(self")[0]
#					if "__init__" in lines[i-1]: lines.pop(i-1)
#					if "__init__" in lines[i-1]: lines.pop(i-2)
#					print(lines[i])
#				if "self.deathrattles = [" in lines[i]:
#					print("Line number", i, lines[i], end="")
#					lines[i] = "\tdeathrattle = " + lines[i].split("= [")[1].split("(self")[0]
#					if "__init__" in lines[i-1]: lines.pop(i-1)
#					if "__init__" in lines[i-1]: lines.pop(i-2)
#					print(lines[i])
#
#			for line in lines:
#				if line: output.write(line)


#for file in os.listdir('Backup'):
#	if file.startswith("HS_") and file.endswith('.py'):
#		print("\n\nPROCESSING FILE", file)
#		with open("Backup\\"+file, 'r', encoding="utf-8") as input, \
#				open("Backup\\Test\\"+file, 'w', encoding="utf-8") as output:
#			lines = []
#			line = input.readline()
#			while line:
#				if '"""' not in line: lines.append(line)
#				line = input.readline()
#
#			inCardSegment, inTrigSegment, curCardSegment, curTrigSegment = False, False, "", ""
#			curOtherSegment = ""
#			lineComment = ''
#
#			for line in lines:
#				if not line.startswith("class "): #It has passed a class definition header
#					if not allTabsandReturnsinLine(line) and not line.startswith("\t"):
#						if isaLineofComment(line):
#							print("A line of comment", line, end="")
#							lineComment += line
#						else:
#							print("Card Trig Ends here", line, end="")
#							inCardSegment = inTrigSegment = False
#					if inCardSegment: curCardSegment += line
#					elif inTrigSegment: curTrigSegment += line
#					else: curOtherSegment += line
#				else: #在重新定义一个类的时候
#					inCardSegment = inTrigSegment = False
#					if "Trig" in line or "Deathrattle" in line or "Aura" in line:
#						print("Another TRIG", line, end="")
#						inTrigSegment = True
#					else:
#						print("Another card", line, end="")
#						inCardSegment = True
#
#					if inTrigSegment:
#						curTrigSegment += "\n\n"
#						curTrigSegment += lineComment
#						lineComment = ''
#						curTrigSegment += line
#					if inCardSegment:
#						curCardSegment += "\n\n"
#						curCardSegment += lineComment
#						lineComment = ''
#						curCardSegment += line
#
#			#print(curTrigSegment)
#			output.write(curOtherSegment)
#			output.write(curTrigSegment)
#			output.write(curCardSegment)

def archiveCardContent(cardName, cardContent): #cardContent is a list of lines in a card
	dict_Archive = {"typeAttri": [], "funcBeforePlayEffect": [], "playEffect": []}
	card = next((card for card in cardPool_All if card.__name__ == cardName), None)
	pos = "typeAttri"
	for line in cardContent:
		if not line.startswith("\tdef") and pos == "typeAttri":
			pass  # 开头的type attribute
		elif line.startswith("\tdef"):
			if "def whenEffective(" in line: pos = "playEffect"
			else: pos = "funcBeforePlayEffect"

		dict_Archive[pos].append(line)
	return card, dict_Archive


def convertFileintoDict(file):
	with open(file, 'r', encoding="utf-8") as inputFile:
		dict_Name2Archive, dict_Name2Obj, isinClass, className, cardContent = {}, {}, False, '', []
		line = inputFile.readline()
		while line:
			if line.startswith("class "): #有一个新的类的时候把旧的类归档
				isinClass = True
				className = line.split("class ")[1].split("(")[0]
				dict_Name2Archive[className] = []
			elif isinClass: dict_Name2Archive[className].append(line)

			line = inputFile.readline()

		for className, cardContent in zip(list(dict_Name2Archive.keys()), list(dict_Name2Archive.values())):
			dict_Name2Obj[className], dict_Name2Archive[className] = archiveCardContent(className, cardContent)
	return dict_Name2Obj, dict_Name2Archive


def getAllClassObjsDict():
	dict_AllObjs, dict_Name2Card = {}, {}
	dict_Name2Archive_Cards, dict_Name2Archive_Collectibles = {}, {}
	for file in os.listdir('.'):
		if file.endswith('.py') and file.startswith("HS_"):
			print(file)
			smallDict_Name2Obj, smallDict_Name2Arhive = convertFileintoDict(file)
			dict_Name2Card.update(smallDict_Name2Obj)
			dict_AllObjs.update(smallDict_Name2Arhive)

			smallDict_Name2Obj_Cards = {name: obj for name, obj in smallDict_Name2Obj.items() if obj}
			smallDict_Name2Arhive_Cards, smallDict_Name2Arhive_Collectibles = {}, {}
			for name, obj in smallDict_Name2Obj_Cards.items():
				smallDict_Name2Arhive_Cards[name] = smallDict_Name2Arhive[name]
				if "~Uncollectible" not in obj.index:
					smallDict_Name2Arhive_Collectibles[name] = smallDict_Name2Arhive[name]
			print(list(smallDict_Name2Obj_Cards.keys()))

			print("\tTotal objs", len(smallDict_Name2Obj))
			print("\tTotal cards included", len(smallDict_Name2Arhive_Cards))
			print("\tTotal collectibles included", len(smallDict_Name2Arhive_Collectibles))

			dict_Name2Archive_Cards.update(smallDict_Name2Arhive_Cards)
			dict_Name2Archive_Collectibles.update(smallDict_Name2Arhive_Collectibles)

	print(len(dict_AllObjs), len(dict_Name2Archive_Cards), len(dict_Name2Archive_Collectibles))


if __name__ == "__main__":
	getAllClassObjsDict()