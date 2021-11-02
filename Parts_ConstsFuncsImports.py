from datetime import datetime
import time, threading, pickle, copy, inspect
import numpy
from numpy.random import choice as numpyChoice
from numpy.random import randint as numpyRandint
from numpy.random import shuffle as numpyShuffle

def getListinDict(dic, key):
	if key not in dic: dic[key] = []
	return dic[key]

def add2ListinDict(obj, dic, key):
	if key in dic: dic[key].append(obj)
	else: dic[key] = [obj]

def removefromListinDict(obj, dic, key):
	if key in dic and obj in dic[key]: dic[key].remove(obj)

def removefrom(obj, ls):
	if obj in ls: ls.remove(obj)

def countTypes(listObj):
	counts = {}
	for a in listObj:
		if a in counts: counts[a] += 1
		else: counts[a] = 1
	return counts
	
def discoverProb(listObj):
	if total := len(listObj):
		counts = {}
		for a in listObj:
			if a in counts: counts[a] += 1
			else: counts[a] = 1
		return list(counts.keys()), [value/total for value in counts.values()]
	else: return [], []


def classforDiscover(initiator):
	Class = initiator.Game.heroes[initiator.ID].Class
	if Class != "Neutral": return Class #如果发现的发起者的职业不是中立，则返回那个职业
	elif initiator.Class != "Neutral": return initiator.Class.split(',')[0] #如果玩家职业是中立，但卡牌职业不是中立，则发现以那个卡牌的职业进行
	else: return initiator.Game.initialClasses[initiator.ID] #如果玩家职业和卡牌职业都是中立，则随机选取一个职业进行发现。

def pickLowestCost(cards):
	ls, i = [], numpy.inf
	for a in cards:
		if a.mana < i: ls, i = [a], a.mana
		elif a.mana == i: ls.append(a)
	return ls

def pickHighestCost(cards):
	ls, i = [], -numpy.inf
	for a in cards:
		if a.mana > i: ls, i = [a], a.mana
		elif a.mana == i: ls.append(a)
	return ls

def pickLowestCostIndices(cards, func=lambda card: True):
	ls, i = [], numpy.inf
	for i, a in enumerate(cards):
		if func(a):
			if a.mana < i: ls, i = [a], a.mana
			elif a.mana == i: ls.append(a)
	return ls

def pickHighestCostIndices(cards, func=lambda card: True):
	ls, i = [], -numpy.inf
	for i, a in enumerate(cards):
		if func(a):
			if a.mana > i: ls, i = [a], a.mana
			elif a.mana == i: ls.append(a)
	return ls

#Not used for finding Hero Head, or Hero Power. Hero cards are included in each expansion folder
def findFilepath(card): #card is an instance
	if card.category == "Dormant":
		if card.minionInside:
			name = card.minionInside.__name__ if inspect.isclass(card.minionInside) else type(card.minionInside).__name__
			return "Images\\%s\\%s.png"%(card.minionInside.index.split('~')[0], name)
		else: return "Images\\%s\\%s.png"%(card.index.split('~')[0], type(card).__name__)
	elif "Option" in card.category:
		return "Images\\Options\\%s.png"%type(card).__name__
	elif card.category in ("Minion", "Weapon", "Spell", "Hero"):  #category == "Weapon", "Minion", "Spell", "Hero", "Power"
		return "Images\\%s\\%s.png"%(card.index.split('~')[0], type(card).__name__.split('__')[0]) #Mutable cards need to be handled
	elif card.category == "Power":
		return "Images\\HeroesandPowers\\%s.png"%type(card).__name__
	
CHN = False

red, green, blue = (1, 0, 0, 1), (0.3, 1, 0.2, 1), (0, 0, 1, 1)
yellow, pink = (1, 1, 0, 1), (1, 0, 1, 1)
darkGreen = (0.3, 0.8, 0.2, 1)
transparent, grey = (1, 1, 1, 0), (0.5, 0.5, 0.5, 1)
black, white = (0, 0, 0, 1), (1, 1, 1, 1)

Classes = ["Demon Hunter", "Druid", "Hunter", "Mage", "Paladin",
		   "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]

SVClasses = ["Forestcraft", "Swordcraft", "Runecraft", "Dragoncraft", "Shadowcraft", "Bloodcraft", "Havencraft",
			"Portalcraft"]
			
BoardIndex = ["1 Classic Ogrimmar", "2 Classic Stormwind", "3 Classic Stranglethorn", "4 Classic Four Wind Valley",
			#"5 Naxxramas", "6 Goblins vs Gnomes", "7 Black Rock Mountain", "8 The Grand Tournament", "9 League of Explorers Museum", "10 League of Explorers Ruins",
			#"11 Corrupted Stormwind", "12 Karazhan", "13 Gadgetzan",
			#"14 Un'Goro", "15 Frozen Throne", "16 Kobolds",
			#"17 Witchwood", "18 Boomsday Lab", "19 Rumble",
			#"20 Dalaran", "21 Uldum Desert", "22 Uldum Oasis", "23 Dragons",
			"24 Outlands", "25 Scholomance Academy", "26 Darkmoon Faire",
			#"27 Barrens", "28 United in Stormwind",
			]