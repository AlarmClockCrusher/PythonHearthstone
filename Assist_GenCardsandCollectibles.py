from HS_Stormwind import Stormwind_Cards
packName = "Stormwind"


Classes = ["Neutral", "Demon Hunter", "Druid", "Hunter", "Mage", "Paladin", "Priest", "Rogue", "Shaman", "Warlock", "Warrior"]
wrapLength = 120
d, d_Collectible = {}, {}
s, s_Collectible = '', ''
prefix_EachLine = "\t\t"

for card in Stormwind_Cards:
	if card.Class not in d: d[card.Class] = [card]
	else: d[card.Class].append(card)
	if "~Uncollectible" not in card.index:
		if card.Class not in d_Collectible: d_Collectible[card.Class] = [card]
		else: d_Collectible[card.Class].append(card)

for Class in Classes:
	s += prefix_EachLine + "#%s\n"%Class
	s_Collectible += prefix_EachLine + "#%s\n"%Class

	line = prefix_EachLine
	for card in d[Class]:
		if len(line + "%s, "%card.__name__) > wrapLength:
			s += line + '\n'
			line = prefix_EachLine + "%s, "%card.__name__
		else: line += "%s, "%card.__name__
	s += line + "\n"

	line = prefix_EachLine
	for card in d_Collectible[Class]:
		if len(line + "%s, " % card.__name__) > wrapLength:
			s_Collectible += line + '\n'
			line = prefix_EachLine + "%s, " % card.__name__
		else: line += "%s, " % card.__name__
	s_Collectible += line + "\n"

print(packName+"_Cards = [")
print(s, end='')
print(']')
print()

print(packName+"_Cards_Collectible = [")
print(s_Collectible, end='')
print(']')
