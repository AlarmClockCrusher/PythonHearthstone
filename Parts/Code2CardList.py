from hearthstone import deckstrings
import json
import string
from Parts.ConstsFuncsImports import *
from Parts.CardTypes import Card

def indexHasClass(index, Class):
	return Class in index.split('~')[1]
	
def canBeGenerated(cardType, SV=0):
	return (SV or not cardType.index.startswith("SV_")) and not "Quest" in cardType.race and \
			not ("Galakrond" in cardType.name or "Galakrond" in cardType.description or "Invoke" in cardType.description or "invoke" in cardType.description) and \
			not "Transfer Student" in cardType.name



class Pools: pass


from HS_Cards.AcrossPacks import AllClasses_AcrossPacks
from HS_Cards.Core import AllClasses_Core
from HS_Cards.Shadows import AllClasses_Shadows
from HS_Cards.Uldum import AllClasses_Uldum
from HS_Cards.Dragons import AllClasses_Dragons
from HS_Cards.Galakrond import AllClasses_Galakrond
from HS_Cards.DemonHunterInitiate import AllClasses_DemonHunterInitiate
from HS_Cards.Outlands import AllClasses_Outlands
from HS_Cards.Academy import AllClasses_Academy, TransferStudent_Dragons, TransferStudent_Academy
from HS_Cards.Darkmoon import AllClasses_Darkmoon
from HS_Cards.Barrens import AllClasses_Barrens
from HS_Cards.Stormwind import AllClasses_Stormwind
from HS_Cards.Alterac import AllClasses_Alterac

from DIY_Cards.DIY_Cards import *


def makeCardPool(monk=0, SV=0):
	cardPool, cardPool_All, info = [], [], ""

	cardPool_All += AllClasses_AcrossPacks #Has the basic hero and hero power definitions.
	cardPool_All += AllClasses_Core
	cardPool_All += AllClasses_Shadows
	cardPool_All += AllClasses_Uldum
	cardPool_All += AllClasses_Dragons
	cardPool_All += AllClasses_Galakrond
	cardPool_All += AllClasses_DemonHunterInitiate
	cardPool_All += AllClasses_Outlands
	cardPool_All += AllClasses_Academy
	cardPool_All += AllClasses_Darkmoon
	cardPool_All += AllClasses_Barrens
	cardPool_All += AllClasses_Stormwind
	cardPool_All += AllClasses_Alterac

	cardPool_All += AllClasses_DIY

	cardPool_All = [class_ for class_ in cardPool_All if issubclass(class_, Card) #and class_.Class
							and class_.category in ("Minion", "Spell", "Weapon", "Hero", "Power")]
	for i, card in enumerate(cardPool_All):
		card.cardID = i
		if hasattr(card, "deathrattle") and card.deathrattle: card.deathrattle.cardType = card
		if card.trigEffect: card.trigEffect.cardType = card
		if hasattr(card, "trigBoard") and card.trigBoard: card.trigBoard.cardType = card
		if hasattr(card, "trigHand") and card.trigHand: card.trigHand.cardType = card
		if hasattr(card, "trigDeck") and card.trigDeck: card.trigDeck.cardType = card

	cardPool = [card for card in cardPool_All if card.Class and "Uncollectible" not in card.index]
	BasicPowers, UpgradedPowers, Classes, ClassesandNeutral, Class2HeroDict = [], [], [], [], {}
	for card in cardPool[:]:
		if card.category == "Hero" and card.index == "LEGACY":
			Classes.append(card.Class)

			ClassesandNeutral.append(card.Class)
			Class2HeroDict[card.Class] = card
			cardPool.remove(card)
		elif card.category == "Power":
			if "Upgraded Hero Power" in card.index: UpgradedPowers.append(card)
			elif "Basic Hero Power" in card.index: BasicPowers.append(card)
			cardPool.remove(card)

	ClassesandNeutral.append("Neutral")
	
	pools = Pools()
	pools.cardPool = cardPool
	pools.Classes = Classes
	pools.ClassesandNeutral = ClassesandNeutral
	pools.Class2HeroDict = Class2HeroDict
	pools.basicPowers = BasicPowers
	pools.upgradedPowers = UpgradedPowers
	
	#print("SV cards included in card pool:", "SV_Basic~Runecraft~4~3~3~Minion~~Vesper, Witchhunter~Accelerate~Fanfare" in cardPool)
	#cardPool本身需要保留各种祈求牌
	pools.MinionsofCost, pools.WeaponsofCost, pools.SpellsofCost = {}, {}, {}
	pools.MinionswithRace = {"Beast": [], "Demon": [], "Dragon": [], "Elemental":[],
							"Murloc": [], "Mech": [], "Pirate":[], "Quilboar": [], "Totem": []}
	if SV:
		SV_Races = ["Officer", "Commander", "Machina", "Natura", "Earth Sigil", "Mysteria", "Artifact", "Levin"]
		for race in SV_Races:
			pools.MinionswithRace[race] = []
	
	pools.ClassCards = {s: [] for s in pools.Classes}
	pools.ClassSpells, pools.ClassMinions = {s: [] for s in pools.Classes}, {s: [] for s in pools.Classes}
	pools.Minions, pools.LegendaryMinions, pools.NeutralCards, pools.NeutralMinions = [], [], [], []
	for card in cardPool: #Fill MinionswithRace
		if canBeGenerated(card, SV=SV):
			if card.category == "Minion":
				if card.race:
					for race in card.race.split(','):
						pools.MinionswithRace[race].append(card)
				add2ListinDict(card, pools.MinionsofCost, card.mana)
				pools.Minions.append(card)
				if "~Legendary" in card.index: pools.LegendaryMinions.append(card)
				pools.NeutralMinions.append(card)
			elif card.category == "Weapon":  add2ListinDict(card, pools.WeaponsofCost, card.mana)
			elif card.category == "Spell": add2ListinDict(card, pools.SpellsofCost, card.mana)
			for Class in card.Class.split(','):
				if Class != "Neutral":
					pools.ClassCards[Class].append(card)
					if card.category == "Spell": pools.ClassSpells[Class].append(card)
					elif card.category == "Minion": pools.ClassMinions[Class].append(card)
				else: pools.NeutralCards.append(card)

	#确定RNGPools
	RNGPools = {"Classes": ['Demon Hunter', 'Hunter', 'Rogue', 'Druid', 'Warrior', 'Paladin', 'Shaman', 'Mage', 'Priest', 'Warlock', ]}
	# 有一些高度通用的随机池，如x-Cost Minions to Summon, "Druid Spells"，直接在这里生成
	for genFunc in (genPool_MinionsofRace, genPool_MinionsofCosttoSummon, genPool_WeaponsofCost, genPool_SpellsofCost,
					genPool_Secrets,
					genPool_ClassCards, genPool_ClassMinions, genPool_ClassSpells, genPool_MinionsasClasstoSummon, ):
		identifier, pool = genFunc(pools)
		if isinstance(identifier, (list, tuple)):
			for key, value in zip(identifier, pool):
				RNGPools[key] = value
		else: RNGPools[identifier] = pool

	for card in cardPool + [TransferStudent_Dragons, TransferStudent_Academy]:
		if hasattr(card, "poolIdentifier"):
			identifier, pool = card.generatePool(pools)
			#发现职业法术一定会生成一个职业列表，不会因为生成某个特定职业法术的牌而被跳过
			if isinstance(identifier, (list, tuple)):
				for key, value in zip(identifier, pool):
					RNGPools[key] = value
			else: RNGPools[identifier] = pool

	return cardPool, cardPool_All, RNGPools, pools.ClassCards, pools.NeutralCards, pools.Class2HeroDict



"""Parse deck code to list of cards"""
cardType2jsonType = {"Minion": "MINION", "Spell": "SPELL", "Weapon": "WEAPON", "Hero": "HERO"}

json_Collectibles = json.loads(open("cards.collectible.json", "r", encoding="utf-8").read())
json_Uncollectible = json.loads(open("cards.json", "r", encoding="utf-8").read())


def typeName2Class(typename, cardPool_All):
	if value := next((value for value in cardPool_All if value.__name__ == typename), None):
		return value
	else: print(typename, " not found")

def decideClassofaDeck(cards):
	# If all Neutral cards, default is "Demon Hunter"; pick the 1st single-Class class card; otherwise, pick the first non-Neutral card
	if Class := next((card.Class for card in cards if card.Class != "Neutral" and ',' not in card.Class), ''):
		return Class
	else: return next((card.Class for card in cards if card.Class != "Neutral"), 'Demon Hunter').split(',')[0]

def parseDeckCode(deckString, Class, Class2HeroDict, cardPool_All):
	deck, deckCorrect, hero = [], False, Class2HeroDict[Class]
	if deckString:
		try:
			if deckString.startswith("names||"):
				names = deckString.split('||')[1:]
				deck = [typeName2Class(name.strip(), cardPool_All) for name in names if name]
			else: deck = decode_deckstring(deckString, cardPool_All)
			deckCorrect = all(obj is not None for obj in deck)
		except Exception as e: print("Parsing encountered error", e)
	else: deck, deckCorrect = [], True
	if deckCorrect:
		hero = Class2HeroDict[decideClassofaDeck(deck)]
	return deck, deckCorrect, hero


def getCardnameFromDbf(dbfId):
	for cardInfo in json_Uncollectible:
		if cardInfo["dbfId"] == dbfId:
			return cardInfo["name"]


def decode_deckstring(s, cardPool, to="List"):
	deckTuple = deckstrings.parse_deckstring(s)[0]
	if to == "string":
		deckList = "["
		for each in deckTuple:
			# each is a tupel (dbfid, number of cards in the deck)
			for i in range(each[1]):
				cardName = getCardnameFromDbf(each[0])
				name_withoutPunctuations = cardName.translate(str.maketrans('', '', string.punctuation))
				name_NoSpace = name_withoutPunctuations.replace(' ', '')
				deckList += name_NoSpace + ', '

		deckList += ']'
		return deckList
	else:  # to == "List"
		deckList = []
		for each in deckTuple:
			for i in range(each[1]):
				cardName = getCardnameFromDbf(each[0])
				name_withoutPunctuations = cardName.translate(str.maketrans('', '', string.punctuation))
				name_NoSpace = name_withoutPunctuations.replace(' ', '')
				className = typeName2Class(name_NoSpace, cardPool)
				deckList.append(className)
		return deckList


def getAnyCardInfofromType(cardType):
	possibleCards = []
	for cardInfo in json_Uncollectible:
		setName = cardType.index.split('~')[0]
		jsonName, cardName = cardInfo["name"], cardType.name
		isCollectibleinJson, isCollectibleinType = "collectible" in cardInfo, "Uncollectible" not in cardType.index
		if "type" in cardInfo:
			jsonType, translatedType = cardInfo["type"], cardType2jsonType[cardType.category]
			if jsonName == cardName and cardInfo["set"] == setName:
				possibleCards.append((cardName, isCollectibleinJson, isCollectibleinType, jsonType, translatedType))
				if isCollectibleinJson == isCollectibleinType and jsonType == translatedType:
					return cardInfo
	return possibleCards


def checktheStatsofCards(cardPool):
	raceAllCapDict = {"Elemental": "ELEMENTAL", "Mech": "MECHANICAL", "Demon": "DEMON", "Murloc": "MURLOC",
					  "Dragon": "DRAGON", "Beast": "BEAST", "Pirate": "PIRATE", "Quilboar": "QUILBOAR",
					  "Totem": "TOTEM",
					  "Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Quilboar,Totem": "ALL"}
	schoolAllCapDict = {"Arcane": "ARCANE", "Fire": "FIRE", "Frost": "FROST", "Nature": "NATURE",
						"Fel": "FEL", "Shadow": "SHADOW", "Holy": "HOLY"}

	exceptionList = []
	for card in cardPool:
		if card.index.startswith("SV_"): continue
		try:
			cardInfo = getAnyCardInfofromType(card)  # Get the name
			if isinstance(cardInfo, list):
				print("Didn't find a match of the card {}/{}".format(card.__name__, card.name))
				print("Possible matches")
				print(cardInfo)
				continue
			# Check the cost of card vs the official json file
			if not (int(cardInfo["cost"]) == card.mana):
				print(card, " has a wrong mana {}|{}".format(cardInfo["cost"], card.mana))
		except Exception as e:
			print(e)
			print("stopped at step 1 {}".format(card))
			continue
		# Will check the category of the cards (Minion, Spell, etc)
		category = card.category
		try:
			if category == "Minion":
				if not (cardInfo["attack"] == card.attack and cardInfo["health"] == card.health):
					print(card, " has a wrong stat:")
					print(card,
						  "Attack: {}|{} Health: {}|{}".format(cardInfo["attack"], card.attack, cardInfo["health"], card.health))
				if "race" in cardInfo:
					if cardInfo["race"] == "All":
						if card.race != "Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Quilboar,Totem":
							print(card,
								  " race should be 'Elemental,Mech,Demon,Murloc,Dragon,Beast,Pirate,Quilboar,Totem'")
					elif raceAllCapDict[card.race] != cardInfo["race"]:
						print(card, " race doesn't match json")
						print(raceAllCapDict[card.race], cardInfo["race"])
				elif card.race: print(card, " shouldn't have race", card.race)
				#Check the card.effects of the minion
				for word in card.Effects.split(','):
					if word and word.split('_')[0] not in \
							("Frozen", "Taunt", "Divine Shield", "Stealth", "Lifesteal", "Spell Damage", "Windfury",
							 "Mega Windfury", "Charge", "Poisonous", "Rush", "Echo", "Reborn", "Evasive",
							 "Can't Attack", "Sweep", "Can't Attack Hero"):
						print(card, " card.indexWord input is wrong {}.".format(word))
			elif category == "Weapon":
				if not (cardInfo["attack"] == card.attack and cardInfo["durability"] == card.durability):
					print(card, " has a wrong stat", cardInfo["attack"], card.attack)
			else:  # Spell
				if "spellSchool" in cardInfo:
					if schoolAllCapDict[card.school] != cardInfo["spellSchool"]:
						print(card, "has a wrong school", cardInfo["spellSchool"], card.school)
				elif card.school: print(card, "shouldn't have school", card.school)
		except Exception as e:
			# print("When checking ", card, e)
			exceptionList.append((card, e))
	return exceptionList


def checkCardStats_Alltogether(cardPool):
	exceptionList = checktheStatsofCards(cardPool)
	# Check if all collectible cards are matched in the json
	for card in cardPool:
		if "Uncollectible" not in card.index:
			for each in json_Collectibles:
				if each["name"] == card.name:
					name_withoutPunctuations = each["name"].translate(str.maketrans('', '', string.punctuation))
					name_NoSpace = name_withoutPunctuations.replace(' ', '')
					if (className := typeName2Class(name_NoSpace, cardPool)) is not card: print(card)
					break

	for exception in exceptionList:
		print("{}".format(exception))


if __name__ == "__main__":
	cardPool, cardPool_All, *_ = makeCardPool()
	from Assist_ArchiveCards import *
	filenames = [name.replace("HS_Cards", '..\\HS_Cards') for name in filenames]
	dicts = getDictsofArchives(lists_AllClasses, filenames)
	dic = dicts["Collectibles"]
	cards = [card for card, archive in dic.items() if "iscover" in card.description]
	deck1, deck2 = cards[:int(len(cards)/2)], cards[int(len(cards)/2):]
	s1 = s2 = 'names'
	for card in deck1: s1 += "||"+card.__name__
	for card in deck2: s2 += "||"+card.__name__
	print(s1)
	print(s2)