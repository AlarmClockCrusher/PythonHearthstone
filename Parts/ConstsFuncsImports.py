from datetime import datetime
import os, time, threading, pickle, copy, inspect, socket, math, itertools
import numpy
from numpy.random import choice as numpyRandomChoice
from numpy.random import randint as numpyRandint
from numpy.random import shuffle as numpyShuffle
import tkinter as tk
from tkinter import ttk, messagebox
import PIL.Image, PIL.ImageTk
from win32clipboard import OpenClipboard, CloseClipboard, EmptyClipboard, SetClipboardText, GetClipboardData

def numpyChoice(a, size=None, replace=True, p=None):
	if size is None: return numpyRandomChoice(a)
	else: return list(numpyRandomChoice(a, size, replace, p))


def getListinDict(dic, key):
	if key not in dic: dic[key] = []
	return dic[key]

def add2ListinDict(obj, dic, key):
	if key in dic: dic[key].append(obj)
	else: dic[key] = [obj]

def removefromListinDict(obj, dic, key):
	if key in dic and obj in dic[key]: dic[key].remove(obj)

#3 options:
	#1  obj in ls? ls.remove
	#2  try: ls.remove() except ValueError
	#3  next(i for i, e in enumerate()) ls.pop()
	#If obj not in ls #2 is 20% slower than #1, #3 is 3 times slower than #1
def removefrom(obj, ls):
	if obj in ls: ls.remove(obj)

#3 options:
	#1  obj in ls? ls.index
	#2  try: ls.index() except ValueError
	#3  next(i for i, e in enumerate())
	#If obj in ls, #2 is 50% FASTER than #1, #3 is 2 times slower than #1
	#If obj NOT in ls, #2 is 50% SLOWER than #1, #3 is 3 times slower than #1
def indin(obj, ls):
	return ls.index(obj) if obj in ls else -1


def countOccurrences(ls):
	counts = {}
	for a in ls:
		if a in counts: counts[a] += 1
		else: counts[a] = 1
	return counts

#当牌库中有不同buff身材的同类随从时，发现的种类仍然是只有那类随从的一种。有可能是优先拿没有buff的。
#打出的飞行管理员可以被对方 的剽窃拿到。打出的有buff的随从只会让对方拿到基础复制
#打出的被禁锢的魔喉也可以触发对方的埋伏，被剽窃拿到，和被小范拿到，触发对面的莫尔杉哨所
#打出的被禁锢的魔喉可以触发连击
#打出休眠的阳鳃鱼人可以触发鱼人招潮者的扳机，也可以触发飞刀杂耍者的扳机。但是始终都不触发狂欢报幕员的扳机
#被复活的休眠阳鳃鱼人也可以正常触发上述的扳机
def discoverProb(ls, cond):
	if ls:
		counts, types2Inds, n = {}, {}, 0
		for i, a in enumerate(ls):
			if cond(a):
				n += 1
				if (typ := a) in counts:
					counts[typ] += 1
					types2Inds[typ].append(i)
				else: counts[typ], types2Inds[typ] = 1, [i]
		return list(counts.keys()), [val/n for val in counts.values()], types2Inds
	else: return [], [], {}

def discoverProb_fromTups(tups):
	if total := len(tups):
		counts, types2Tups = {}, {}
		for tup in tups:
			if (typ := tup[0]) in counts:
				counts[typ] += 1
				types2Tups[typ].append(tup)
			else: counts[typ], types2Tups[typ] = 1, [tup]
		return list(counts.keys()), [val/total for val in counts.values()], types2Tups
	else: return [], [], {}
	
#Given a list of objs to sort, return the list that
#contains the targets in the right order to trigger.
def objs_SeqSorted(objs):
	order = numpy.array([obj.seq for obj in objs]).argsort()
	return [objs[i] for i in order], order

def class4Discover(initiator):
	Class = initiator.Game.heroes[initiator.ID].Class
	if Class != "Neutral": return Class #如果发现的发起者的职业不是中立，则返回那个职业
	elif initiator.Class != "Neutral": return initiator.Class.split(',')[0] #如果玩家职业是中立，但卡牌职业不是中立，则发现以那个卡牌的职业进行
	else: return initiator.Game.initialClasses[initiator.ID] #如果玩家职业和卡牌职业都是中立，则随机选取一个职业进行发现。


def secrets2Discover(initiator, toPutonBoard=False):
	HeroClass, Class = initiator.Game.heroes[initiator.ID].Class, initiator.Class
	classes = ("Hunter", "Mage", "Paladin", "Rogue")
	if HeroClass in classes: key = HeroClass + " Secrets"
	elif Class in classes: key = Class + " Secrets"
	else: key = classes[datetime.now().microsecond % len(classes)] + " Secrets"
	if toPutonBoard:
		cond = initiator.Game.Secrets.sameSecretExists
		return [card for card in initiator.rngPool(key) if not cond(card, initiator.ID)]
	else: return initiator.rngPool(key)


def pickObjs_LowestAttr(cards, cond=lambda card: True, attr="mana"):
	ls, x = [], numpy.inf
	for a in cards:
		if cond(a):
			if (num := a.__dict__[attr]) < x: ls, x = [a], num
			elif num == x: ls.append(a)
	return ls

def pickObjs_HighestAttr(cards, cond=lambda card: True, attr="mana"):
	ls, x = [], -numpy.inf
	for a in cards:
		if cond(a):
			if (num := a.__dict__[attr]) > x: ls, x = [a], num
			elif num == x: ls.append(a)
	return ls

def pickInds_LowestAttr(cards, cond=lambda card: True, attr="mana"):
	ls, x = [], numpy.inf
	for i, a in enumerate(cards):
		if cond(a):
			if (num := a.__dict__[attr]) < x: ls, x = [i], num
			elif num == x: ls.append(i)
	return ls
	
def pickInds_HighestAttr(cards, cond=lambda card: True, attr="mana"):
	ls, x = [], -numpy.inf
	for i, a in enumerate(cards):
		if cond(a):
			if (num := a.__dict__[attr]) > x: ls, x = [i], num
			elif num == x: ls.append(i)
	return ls

#Not used for finding Hero Head, or Hero Power. Hero cards are included in each expansion folder
def findFilepath(card): #card is an instance
	if "Option" in card.category:
		return ".\Images\\Options\\%s.png"%type(card).__name__
	elif card.category in ("Minion", "Dormant", "Weapon", "Spell", "Hero"):
		return ".\Images\\%s\\%s.png"%(card.index.split('~')[0], type(card).__name__.split('__')[0]) #Mutable cards need to be handled
	elif card.category == "Power":
		return ".\Images\\HeroesandPowers\\%s.png"%type(card).__name__


def getPILPhotoImage(master=None, filePath='', size=()):
	if size: img = PIL.Image.open(filePath).resize(size)
	else: img = PIL.Image.open(filePath)
	return PIL.ImageTk.PhotoImage(img)

def pickleObj2Bytes(obj):
	return pickle.dumps(obj, 0)

def unpickleBytes2Obj(s):
	return pickle.loads(s)

def recv_PossibleLongData(sock):
	totalData = b""
	while True:
		try: totalData += sock.recv(1024)
		except ConnectionError: totalData = b""
		except OSError:
			print("While recving, sock is actually not connected", sock)
			totalData = b""
		#Empty totalData will also break the loop
		if not totalData.startswith(b"MsgStart") or totalData.endswith(b"__MsgEnd"):
			break
	return totalData.replace(b"MsgStart", b'').replace(b"__MsgEnd", b'')

def send_PossiblePadding(sock, data):
	if len(data) > 1000: data = b"MsgStart" + data + b"__MsgEnd"
	try: sock.sendall(data)
	except ConnectionError as e: print("{} while sending info".format(e))



"""Generate RNG pool templates"""
def genPool_MinionsofRace(pools):
	return [race+"s" for race in pools.MinionswithRace], list(pools.MinionswithRace.values())

def genPool_MinionsofCosttoSummon(pools):
	return ["Minions to Summon Costs"] + ["%d-Cost Minions to Summon" % cost for cost in pools.MinionsofCost], \
		   [sorted(pools.MinionsofCost.keys())] + list(pools.MinionsofCost.values())

def genPool_WeaponsofCost(pools):
	return ["Weapons Costs"] + ["%d-Cost Weapons"%cost for cost in pools.WeaponsofCost],\
		   	[sorted(pools.WeaponsofCost.keys())] + list(pools.WeaponsofCost.values())

def genPool_SpellsofCost(pools):
	return ["Spells Costs"] + ["%d-Cost Spells"%cost for cost in pools.SpellsofCost],\
		   	[sorted(pools.SpellsofCost.keys())] + list(pools.SpellsofCost.values())

def genPool_ClassCards(pools):
	return [Class + " Cards" for Class in pools.Classes], list(pools.ClassCards.values())

def genPool_ClassMinions(pools):
	return [Class + " Minions" for Class in pools.Classes], list(pools.ClassMinions.values())

def genPool_ClassSpells(pools):
	return [Class + " Spells" for Class in pools.Classes], list(pools.ClassSpells.values())


def genPool_MinionsasClasstoSummon(pools):
	neutralMinions = pools.NeutralMinions
	return ["Minions as %s to Summon"%Class for Class in pools.Classes], \
		   [pools.ClassMinions[Class] + neutralMinions for Class in pools.Classes]

def genPool_Secrets(pools):
	classes, lists = [], []
	for Class, cards in pools.ClassCards.items():
		if secrets := [card for card in cards if card.race == "Secret"]:
			classes.append(Class + " Secrets")
			lists.append(secrets)
	return classes, lists

def genPool_CardsasClass(pools):
	return ["Cards as %s" % Class for Class in pools.ClassCards], \
			[cards + pools.NeutralCards for cards in list(pools.ClassCards.values())]

def genPool_MinionsofRaceasClass(pools, race):
	neutralMinions = [card for card in pools.NeutralMinions if card.race == race]
	classCards = {Class: [card for card in cards if race in card.race] for Class, cards in pools.ClassCards.items()}
	return [race+"s as "+Class for Class in classCards], [minions+neutralMinions for minions in classCards.values()]

def genPool_CertainCardsasClass(pools, word, cond):
	neutralCards = [card for card in pools.NeutralCards if cond(card)]
	classCards = {Class: [card for card in cards if cond(card)] for Class, cards in pools.ClassCards.items()}
	return [word+" Cards as "+Class for Class in classCards], [cards+neutralCards for cards in classCards.values()]

def genPool_CertainMinionsasClass(pools, word, cond):
	neutralMinions = [card for card in pools.NeutralCards if card.category == "Minion" and cond(card)]
	classCards = {Class: [card for card in cards if card.category == "Minion" and cond(card)] for Class, cards in pools.ClassCards.items()}
	return [word+" Minions as "+Class for Class in classCards], [minions+neutralMinions for minions in classCards.values()]

def genPool_CertainMinions(pools, word, cond):
	return word+" Minions", [card for card in pools.Minions if cond(card)]


"""GUI"""
red, green, blue = (1, 0, 0, 1), (0.3, 1, 0.2, 1), (0, 0, 1, 1)
yellow, pink = (1, 1, 0, 1), (1, 0, 1, 1)
darkGreen = (0.3, 0.8, 0.2, 1)
transparent, grey = (1, 1, 1, 0), (0.5, 0.5, 0.5, 1)
black, white = (0, 0, 0, 1), (1, 1, 1, 1)
collectionTrayColor, collectionTraySelectedColor = (0.99, 0.93, 0.70, 1), (1, 0.42, 1, 1)
ZoomInCard_X, ZoomInCard1_Y, ZoomInCard2_Y, ZoomInCard_Z = -11.1, -1.5, 4.25, 20

Classes = ["Demon Hunter", "Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]
ClassesandNeutral = Classes + ["Neutral"]
Classes2HeroeNames = {"Demon Hunter": "Illidan", "Druid": "Malfurion", "Hunter": "Rexxar", "Mage": "Jaina", "Paladin": "Uther",
					  "Priest": "Anduin", "Rogue": "Valeera", "Shaman": "Thrall", "Warlock": "Guldan", "Warrior": "Garrosh"}
filePath_HeroBlank = "Images\\HeroesandPowers\\Unknown.png"

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

class Game_PlaceHolder:
	name, mana, category, race, school  = "Game", -1, "Spell", "", ""
	name_CN = "游戏进程"
	def __init__(self, Game, ID):
		self.Game, self.ID = Game, ID
		self.name, self.category, self.race, self.school = "Game", "Spell", "", ""
		self.mana, self.creator = -1, None
		self.onBoard = self.inHand = self.inDeck = False
		self.index = "CORE~~Spell~1~Holy~Game_PlaceHolder"
		self.enchantments = self.trigsBoard = self.trigsHand = self.trigsDeck = self.deathrattles = []
		self.btn = None

	def text(self): return ''


lang = "CN"

translateTable = {
	"Created by:\n":
		{"CN": "创建者:\n", },
	"Deck: {}\nHand: {}":
		{"CN": "牌库: {}\n手牌: {}", },
	"Your deck is full":
		{"CN": "你的套牌已满", },
	"At most 1 copy of Legendary card in the deck" :
		{"CN": "套牌中最多只能有一张相同的传说卡牌", },
	"Can't have >2 copies in the same deck":
		{"CN": "套牌中最多只能有2张相同的卡牌", },
	"Deck 1 incorrect":
		{"CN": "玩家1的套牌代码有误", },
	"Deck 2 incorrect":
		{"CN": "玩家2的套牌代码有误", },
	"Deck 1&2 incorrect":
		{"CN": "玩家1与玩家2的套牌代码均有误", },
	"No card match":
		{"CN": "没有符合条件的卡牌", },
	"Back":
		{"CN": "返回"},
	"Import":
		{"CN": "导入"},
	"Clear":
		{"CN": "清空"},
	"Your deck code: (DO NOT DELETE THIS LINE)":
		{"CN": "你的套牌代码：（不要删除该行）", },
	"----------------------(DO NOT DELETE THIS LINE)":
		{"CN": "----------------------（不要删除该行）", },
	"Your opponent's deck code in 1P mode: (DO NOT DELETE THIS LINE)":
		{"CN": "单人模式下玩家2的的套牌代码：（不要删除该行）", },
	"Your deck code/input format is incorrect\n'Deck Codes.txt' has been reset with default deck":
		{"CN": "你的套牌代码或输入格式有误\n'Deck Codes.txt'已经使用默认套牌代码重置", },
	#Online Game
	"Server IP Address: {}\nServer Query Port: {}\nPlayer ID: {}":
		{"CN": "服务器IP地址: {}\n服务器端口: {}\n玩家ID: {}", },
	"GuestID CANNOT have ':' or '---'":
		{"CN": "用户ID不能含有英文的‘:’和‘---’"},
	"This ID is taken":
		{"CN": "该ID已被占用，重新命名"},
	"You have the same player ID as someone else.\nDisconnect and change your ID":
		{"CN": "你的ID与其他人重复了。请断开并修改ID"},
	"No room for more guests for now":
		{"CN": "暂时不能容纳更多用户了"},
	"See Each \nOther's Hand":
		{"CN": "双方手牌\n互相可见", },
	"Server IP Address":
		{"CN": "服务器IP地址", },
	"Query Port":
		{"CN": "接入端口", },
	"Player ID":
		{"CN": "玩家ID", },
	"Edit":
		{"CN": "修改", },
	"Update":
		{"CN": "更新", },
	"Connect":
		{"CN": "连接", },
	"Disconnect":
		{"CN": "断开", },
	"Can't ping the address ":
		{"CN": "无法连通服务器IP地址", },
	"Can't connect to the query port":
		{"CN": "无法连接到给出的接入端口", },
	"Change your ID while not connected":
		{"CN": "你只能在未连接状态下更改ID", },
	"You have disconnected from the server":
		{"CN": "你已经从服务器断开连接", },
	"You must exit the current table before joining another":
		{"CN": "加入其他桌子前，你必须退出当前的桌子", },
	"Table owner ID doesn't match an owned table":
		{"CN": "使用的桌子拥有者ID与不在酒馆内桌子拥有者之中", },
	"Cancel the table you reserved before proceeding":
		{"CN": "你需要首先取消当前预订的桌子", },
	"Exit the table you joined before proceeding":
		{"CN": "你需要首先退出当前加入的桌子", },
	"Reserve":
		{"CN": "预约桌子", },
	"Cancel":
		{"CN": "取消预约", },
	"Join":
		{"CN": "加入对局", },
	"Exit":
		{"CN": "退出牌桌", },
	"Spectate":
		{"CN": "旁观对局", },
	"Concede":
		{"CN": "认输", },
	"Your ID doesn't match the record":
		{"CN": "你的ID与记录不符合", },
	"Joined table. Waiting for table owner to start":
		{"CN": "成功加入牌桌。等待牌桌拥有者开始", },
	"Someone joined your table":
		{"CN": "有人加入了你的牌桌", },
	"Player 1 Conceded!":
		{"CN": "玩家1认输了", },
	"Player 2 Conceded!":
		{"CN": "玩家2认输了", },
	"":
		{"CN": "", },

}


def translate(s, lang):
	if lang == "EN": return s
	try: return translateTable[s][lang]
	except KeyError: return s


def resetDeckCodeFile(lang):
	with open("Deck Codes.txt", 'w', encoding="utf-8") as inputFile:
		inputFile.write(translate("Your deck code: (DO NOT DELETE THIS LINE)", lang)+'\n')
		inputFile.write("names||Fireball||Elven Archer||Argent Squire||Combustion||Arcane Shot||Ace Hunter Kreen||Fireball"+'\n')
		inputFile.write(translate("----------------------(DO NOT DELETE THIS LINE)", lang)+'\n')
		inputFile.write(translate("Your opponent's deck code in 1P mode: (DO NOT DELETE THIS LINE)", lang)+'\n')
		inputFile.write("names||Rise to the Occasion||Elven Archer||Argent Squire||Adorable Infestation||Fireball||Trueaim Crescent||Anetheron||Amulet of Undying"+'\n')

#Load the default deck codes
default1, default2 = [''], ['']

def loadDefault1andDefault2():
	file = open("Deck Codes.txt", 'r', encoding="utf-8")
	try:
		file.readline()
		if line := file.readline(): default1[0] = line
		else: raise IndexError
		file.readline()
		file.readline()
		if line := file.readline(): default2[0] = line
		else: raise IndexError
	except IndexError:
		print("IndexError while loading deck code file. Resetting")
		file.close()
		resetDeckCodeFile(lang)
		loadDefault1andDefault2()

loadDefault1andDefault2()
DefaultDeckCode1, DefaultDeckCode2 = default1[0], default2[0]