import os
from Parts_Code2CardList import *
from Run_GenPools_BuildDecks import makeCardPool

def checkifCardHasFig(cardPool):
	for card in cardPool:
		filePath = ''
		if "__" in card.__name__:
			cardName = card.__name__.split('_')[0]
			filepath = "Images\\%s\\%s.png"%(card.index.split('~')[0], cardName)
		else:
			if card.category == "Power": filepath = "Images\\HeroesandPowers\\%s.png"%card.__name__
			else: filepath = "Images\\%s\\%s.png"%(card.index.split('~')[0], card.__name__)
			
		if not os.path.exists(filepath):
			print("No image for", card.__name__, filePath, os.path.exists(filepath), )
			

def checkifFigHasCard(cardPool):
	expansions2Include = ['THE_BARRENS', 'CORE', 'BLACK_TEMPLE', 'SCHOLOMANCE', 'DARKMOON_FAIRE', 'STORMWIND']
	#expansions2Include = []
	#for card in cardPool:
	#	if (expansion := card.index.split("~")[0]) not in expansions2Include:
	#		expansions2Include.append(expansion)
	print("Expansions included are:", expansions2Include)

	cardNamePool = [card.__name__ for card in cardPool]
	for folder in os.listdir('Images'):
		if "." not in folder and "Option" not in folder and folder in expansions2Include:
			for file in os.listdir("Images\\"+folder):
				cardName = file.split('.')[0].split("__")[0]
				if cardName not in cardNamePool:
					print("Card not found for fig:", "Images\\"+folder+"\\"+cardName)

def generateMaterialInventory():
	with open("MaterialInventory.txt", "w") as outputFile:
		for file in os.listdir("."):
			if (file.endswith(".py") and file != "Run_GetUpdates.py") or file.endswith(".json"):
				s = file + '---' + str(os.path.getsize(file)) + '\n'
				outputFile.write(s)

		for folder in ("Images", "TexCards", "Models"):
			for root, dirs, files in os.walk(folder, topdown=False):
				for name in files:
					filePath = os.path.join(root, name)
					s = filePath + '---' + str(os.path.getsize(filePath)) + '\n'
					outputFile.write(s)

	print("Finished generating material inventory for user to get updates")


if __name__ == "__main__":
	cardPool, cardPool_All, RNGPools = makeCardPool()
	checkifCardHasFig(cardPool_All)
	checkifFigHasCard(cardPool_All)
	checkCardStats_Alltogether()
	generateMaterialInventory()