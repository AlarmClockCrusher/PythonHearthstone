import os

for file in os.listdir('.'):
	if file.endswith(".py") and file.startswith("HS_"):
		print(file)
		with open(file, 'r', encoding="utf-8") as inputFile, \
			open("Backup\\"+file, 'w', encoding="utf-8") as outputFile:
			s = [(line := inputFile.readline())]
			while line: s.append((line := inputFile.readline()))

			s_New, inEffect, num2Remove = [], False, 0
			for i, line in enumerate(s):
				if "def whenEffective" in line:
					inEffect = True
				elif "def " in line or line.startswith("class "):
					inEffect = False

				if "return None" in line and inEffect: num2Remove += 1
				else: s_New.append(line)

			for line in s_New: outputFile.write(line)
			print(num2Remove)