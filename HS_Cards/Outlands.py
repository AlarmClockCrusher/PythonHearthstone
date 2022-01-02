from Parts.CardTypes import *
from Parts.TrigsAuras import *
from HS_Cards.AcrossPacks import ExcessMana
from HS_Cards.Core import WaterElemental, FieryWarAxe


class GameRuleAura_KaynSunfury(GameRuleAura):
	def auraAppears(self): self.keeper.Game.rules[self.keeper.ID]["Ignore Taunt"] += 1
		
	def auraDisappears(self): self.keeper.Game.rules[self.keeper.ID]["Ignore Taunt"] -= 1
		
	
class ManaAura_YsielWindsinger(ManaAura):
	to = 1
	def applicable(self, target): target.category == "Spell" and target.ID == self.keeper.ID
		
	
class ManaAura_KanrethadEbonlocke(ManaAura):
	by = -1
	def applicable(self, target): return target.ID == self.keeper.ID and "Demon" in target.race
		
	
class Death_RustswornInitiate(Deathrattle):
	description = "Deathrattle: Summon a 1/1 Impcaster with Spell Damage +1"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(Impcaster(kpr.Game, kpr.ID))
		
	
class Death_TeronGorefiend(Deathrattle):
	description = "Deathrattle: Resummon all destroyed minions with +1/+1"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		game, ID = (kpr := self.keeper).Game, kpr.ID
		if self.memory:
			kpr.giveEnchant((minions := [game.fabCard(tup, ID, kpr) for tup in self.memory]), 1, 1,
							   source=TeronGorefiend, add2EventinGUI=False)
			kpr.summon(minions)
		
	
class Death_DisguisedWanderer(Deathrattle):
	description = "Deathrattle: Summon a 9/1 Inquisitor"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(RustswornInquisitor(kpr.Game, kpr.ID))
		
	
class Death_RustswornCultist(Deathrattle):
	description = "Deathrattle: Summon a 1/1 Demon"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(RustedDevil(kpr.Game, kpr.ID))
		
	
class Death_Alar(Deathrattle):
	description = "Deathrattle: Summon a 0/3 Ashes of Al'ar that resurrects this minion on your next turn"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(AshesofAlar(kpr.Game, kpr.ID))
		
	
class Death_DragonmawSkyStalker(Deathrattle):
	description = "Deathrattle: Summon a 3/4 Dragonrider"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(Dragonrider(kpr.Game, kpr.ID))
		
	
class Death_ScrapyardColossus(Deathrattle):
	description = "Deathrattle: Summon a 7/7 Felcracked Colossus with Taunt"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(FelcrackedColossus(kpr.Game, kpr.ID))
		
	
class Death_FelSummoner(Deathrattle):
	description = "Deathrattle: Summon a random Demon from your hand"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.try_SummonfromOwn(hand_deck=0, cond=lambda card: "Demon" in card.race)
		
	
class Death_CoilfangWarlord(Deathrattle):
	description = "Deathrattle: Summon a 5/9 Warlord with Taunt"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(ConchguardWarlord(kpr.Game, kpr.ID))
		
	
class Death_ArchsporeMsshifn(Deathrattle):
	description = "Deathrattle: Shuffle 'Msshi'fn Prime' into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).shuffleintoDeck(MsshifnPrime(kpr.Game, kpr.ID))
		
	
class Death_Helboar(Deathrattle):
	description = "Deathrattle: Give a random Beast in your hand +1/+1"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		if beasts := [card for card in self.keeper.Game.Hand_Deck.hands[self.keeper.ID] \
					  if "Beast" in card.race and card.mana > 0]:
			self.keeper.giveEnchant(numpyChoice(beasts), 1, 1, source=Helboar, add2EventinGUI=False)
		
	
class Death_AugmentedPorcupine(Deathrattle):
	description = "Deathrattle: Deal this minion's Attack damage randomly split among all enemies"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		minion, side = self.keeper, 3 - self.keeper.ID
		for _ in range(max(0, minion.attack)):
			if minions := minion.Game.charsAlive(side): minion.dealsDamage(numpyChoice(minions), 1)
			else: break
		
	
class Death_ZixorApexPredator(Deathrattle):
	description = "Deathrattle: Shuffle 'Zixor Prime' into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).shuffleintoDeck(ZixorPrime(kpr.Game, kpr.ID))
		
	
class Death_AstromancerSolarian(Deathrattle):
	description = "Deathrattle: Shuffle 'Solarian Prime' into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).shuffleintoDeck(SolarianPrime(kpr.Game, kpr.ID))
		
	
class Death_Starscryer(Deathrattle):
	description = "Deathrattle: Draw a spell"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.drawCertainCard(lambda card: card.category == "Spell")
		
	
class Death_MurgurMurgurgle(Deathrattle):
	description = "Deathrattle: Shuffle 'Murgurgle Prime' into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).shuffleintoDeck(MurgurglePrime(kpr.Game, kpr.ID))
		
	
class Death_LibramofWisdom(Deathrattle):
	description = "Deathrattle: 'Libram of Wisdom' spell to your hand'"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.addCardtoHand(LibramofWisdom, self.keeper.ID)
		
	
class Death_ReliquaryofSouls(Deathrattle):
	description = "Deathrattle: Shuffle 'Reliquary Prime' into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).shuffleintoDeck(ReliquaryPrime(kpr.Game, kpr.ID))
		
	
class Death_Akama(Deathrattle):
	description = "Deathrattle: Shuffle 'Akama Prime' into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).shuffleintoDeck(AkamaPrime(kpr.Game, kpr.ID))
		
	
class Death_CursedVagrant(Deathrattle):
	description = "Deathrattle: Summon a 7/5 Shadow with Stealth"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(CursedShadow(kpr.Game, kpr.ID))
		
	
class Death_LadyVashj(Deathrattle):
	description = "Deathrattle: Shuffle 'Vashj Prime' into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).shuffleintoDeck(VashjPrime(kpr.Game, kpr.ID))
		
	
class Death_VividSpores(Deathrattle):
	description = "Deathrattle: Resummon this minion'"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		# This Deathrattle can't possibly be triggered in hand
		(kpr := self.keeper).summon(type(kpr)(kpr.Game, kpr.ID))
		
	
class Death_KanrethadEbonlocke(Deathrattle):
	description = "Deathrattle: Shuffle 'Kanrethad Prime' into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).shuffleintoDeck(KanrethadPrime(kpr.Game, kpr.ID))
		
	
class Death_EnhancedDreadlord(Deathrattle):
	description = "Deathrattle: Summon a 5/5 Dreadlord with Lifesteal"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(DesperateDreadlord(kpr.Game, kpr.ID))
		
	
class Death_KargathBladefist(Deathrattle):
	description = "Deathrattle: Shuffle 'Kargath Prime' into your deck"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).shuffleintoDeck(KargathPrime(kpr.Game, kpr.ID))
		
	
class Death_ScrapGolem(Deathrattle):
	description = "Deathrattle: Gain Armor equal to this minion's Attack"
	def effect(self, signal, ID, subject, target, num, comment, choice):
		self.keeper.giveHeroAttackArmor(self.keeper.ID, armor=num)
		
	
class Trig_Imprisoned(Trig_Countdown):
	signals, counter = ("TurnStarts",), 2
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID  # 会在我方回合开始时进行苏醒
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if self.counter < 1:
			self.keeper.losesTrig(self, trigType="TrigBoard")
			self.keeper.awaken()
		
	
class Trig_InfectiousSporeling(TrigBoard):
	signals = ("MinionTookDamage",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr and target.aliveonBoard()
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).transform(target, InfectiousSporeling(kpr.Game, target.ID))
		
	
class Trig_SoulboundAshtongue(TrigBoard):
	signals = ("MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return target is self.keeper
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).dealsDamage(kpr.Game.heroes[kpr.ID], num)
		
	
class Trig_BonechewerBrawler(TrigBoard):
	signals = ("MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(BonechewerBrawler, 2, 0))
		
	
class Trig_MoargArtificer(TrigBoard):
	signals = ("FinalDmgonMinion?",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.onBoard and target.category == "Minion" and subject.category == "Spell" and num[0] > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		num[0] += num[0]
		
	
class Trig_BlisteringRot(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID and kpr.health > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		#假设召唤的Rot只是一个1/1，然后接受buff.而且该随从生命值低于1时不能触发
		#假设攻击力为负数时，召唤物的攻击力为0
		if minion := kpr.summon(LivingRot(kpr.Game, kpr.ID)):
			kpr.setStat(minion, (max(0, kpr.attack), kpr.health), source=BlisteringRot)
		
	
class Trig_Magtheridon(Trig_Countdown):
	signals, counter = ("ObjDied",), 3
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and isinstance(target, HellfireWarder) and target.ID != kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		game = self.keeper.Game
		if self.counter < 1:
			self.keeper.losesTrig(self, trigType="TrigBoard")
			game.kill(self.keeper, game.minionsonBoard())
			game.awaken()
		
	
class Trig_Replicatotron(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if neighbors := kpr.Game.neighbors2(kpr)[0]:
			kpr.transform(numpyChoice(neighbors), kpr.copyCard(kpr, kpr.ID))
		
	
class Trig_AshesofAlar(TrigBoard):
	signals = ("TurnStarts",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).transform(kpr, Alar(kpr.Game, kpr.ID))
		
	
class Trig_BonechewerVanguard(TrigBoard):
	signals = ("MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target is kpr and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveEnchant(kpr, statEnchant=Enchantment_Exclusive(BonechewerVanguard, 2, 0))
		
	
class Trig_KaelthasSunstrider(Trig_Countdown):
	signals, counter = ("CardBeenPlayed", "NewTurnStarts"), 2
	def resetCount(self, useOrig=True):
		numSpells = self.keeper.Game.Counters.examCardPlays(self.keeper.ID, turnInd=self.keeper.Game.turnInd, veri_sum_ls=1, cond=lambda tup: tup[
																																				 0].category == "Sepll")
		self.counter = 2 - numSpells % 3
		if not self.counter: self.startAura() #只会在满足条件的时候启动光环，但是光环被消耗或过期时不会有反应，而由生成的一次性光环处理，然后通知这个扳机
		
	def disconnect(self):
		trigs = self.keeper.Game.trigsBoard[self.keeper.ID]
		for sig in self.signals: removefromListinDict(self, trigs, sig)
		self.removeAura()
		
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and (signal == "NewTurnStarts" or (comment == "Spell" and ID == kpr.ID))
		
	def startAura(self):
		#产生一次性的光环时，需要让那个光环携带凯尔萨斯这个随从的reference，从而那个光环因使用或者过期而消失时可以抒随从身上的光环也去掉
		self.keeper.auras.append(aura := GameManaAura_KaelthasSunstrider(self.keeper.Game, self.keeper.ID, self.keeper))
		aura.auraAppears()
		self.keeper.btn.effectChangeAni("Aura")
		
	def removeAura(self):
		#只会在随从自己disappear从而扳机取消时引用。这个光环被法术消耗掉的时候由GameManaAura_KaelthasSunstrider自行处理
		for aura in self.keeper.auras[:]:
			if isinstance(aura, GameManaAura_KaelthasSunstrider):
				aura.auraDisappears()
				removefrom(aura, self.keeper.auras)
		self.keeper.btn.effectChangeAni("Aura")
		
	def trig(self, signal, ID, subject, target, num, comment, choice):
		if self.canTrig(signal, ID, subject, target, num, comment, choice):
			counter = self.counter
			self.resetCount()
			if counter != self.counter and (btn := self.keeper.btn):
				btn.GUI.seqHolder[-1].append(btn.icons["Hourglass"].seqUpdateText())
		
	
class Trig_DemonicBlast(Trig_Countdown):
	signals, counter = ("HeroUsedAbility",), 2
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return subject is self.keeper
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		power_Old = self.keeper
		if self.counter < 1:
			power = power_Old.powerReplaced
			power.ID = power_Old.ID
			power.replacePower()
		elif power_Old.btn:
			GUI = power_Old.btn.GUI
			texture = GUI.loader.loadTexture("Images\\HeroesandPowers\\DemonicBlast.png")
			np_CardImage, np_Card = power_Old.btn.models["cardImage"], power_Old.btn.models["card"]
			GUI.seqHolder[-1].append(GUI.FUNC(np_CardImage.setTexture, np_CardImage.findTextureStage('*'), texture, 1))
			GUI.seqHolder[-1].append(GUI.FUNC(np_Card.setTexture, np_Card.findTextureStage('*'), texture, 1))
		
	
class Trig_PriestessofFury(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		minion, side = kpr, 3 - kpr.ID
		for _ in range(6):
			if objs := minion.Game.charsAlive(side): minion.dealsDamage(numpyChoice(objs), 1)
			else: break
		
	
class Trig_PitCommander(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).try_SummonfromOwn(kpr.pos + 1, cond=lambda card: "Demon" in card.race)
		
	
class Trig_Ironbark(TrigHand):
	signals = ("ManaXtlsCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_Bogbeam(TrigHand):
	signals = ("ManaXtlsCheck",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.inHand and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class Trig_MarshHydra(TrigBoard):
	signals = ("MinionAttackedMinion", "MinionAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and subject is kpr
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("8-Cost Minions")), kpr.ID)
		
	
class Trig_PackTactics(Trig_Secret):
	signals = ("MinionAttacksMinion", "HeroAttacksMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.ID != kpr.Game.turn and target[0].ID == kpr.ID and kpr.Game.space(kpr.ID) > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		keeper = self.keeper
		keeper.summon([keeper.copyCard(target[0], keeper.ID, 3, 3) for _ in range(type(keeper).num)], position=target[0].pos+1)
		
	
class Trig_Evocation(TrigHand):
	signals, changesCard, description = ("TurnEnds",), True, "At the end of your turn, discard this"
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.inHand #They will be discarded at the end of any turn
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Hand_Deck.discard(kpr.ID, kpr)
		
	
class Trig_ApexisSmuggler(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return (kpr := self.keeper).onBoard and ID == kpr.ID and kpr.Game.cardinPlay.race == "Secret"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).discoverNew('', poolFunc=lambda: self.rngPool(class4Discover(kpr) + " Spells"))
		
	
class Trig_NetherwindPortal(Trig_Secret):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		game, Id = kpr.Game, kpr.ID
		return comment == "Spell" and Id != game.turn == ID and game.space(Id) > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(numpyChoice(self.rngPool("4-Cost Minions to Summon"))(kpr.Game, kpr.ID))
		
	
class Trig_UnderlightAnglingRod(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("Murlocs")), kpr.ID)
		
	
class Trig_SethekkVeilweaver(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and ID == kpr.ID and len(target) == 1 and target[0].category == "Minion" and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("Priest Spells")), kpr.ID)
		
	
class Trig_DragonmawOverseer(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		if minions := kpr.Game.minionsonBoard(kpr.ID, exclude=kpr):
			kpr.giveEnchant(numpyChoice(minions), statEnchant=Enchantment_Exclusive(DragonmawOverseer, 2, 2))
		
	
class Trig_SkeletalDragon(TrigBoard):
	signals = ("TurnEnds",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.onBoard and ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).addCardtoHand(numpyChoice(self.rngPool("Dragons")), kpr.ID)
		
	
class Trig_Ambush(Trig_Secret):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		game, Id = kpr.Game, kpr.ID
		return comment == "Minion" and Id != game.turn == ID and game.space(Id) > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).summon(BrokenAmbusher(kpr.Game, kpr.ID))
		
	
class Trig_Bamboozle(Trig_Secret):
	signals = ("MinionAttacksMinion", "HeroAttacksMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return kpr.ID != kpr.Game.turn and target[0].ID == kpr.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		newMinion = kpr.newEvolved(type(target[0]).mana, by=3, ID=kpr.ID)
		self.keeper.transform(target[0], newMinion)
		if target[0] is target[1]: target[0] = target[1] = newMinion
		else: target[0] = newMinion
		
	
class Trig_DirtyTricks(Trig_Secret):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return comment == "Spell" and kpr.ID != kpr.Game.turn == ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		kpr.Game.Hand_Deck.drawCard(kpr.ID)
		kpr.Game.Hand_Deck.drawCard(kpr.ID)
		
	
class Trig_ShadowjewelerHanar(TrigBoard):
	signals = ("CardBeenPlayed",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return (obj := self.keeper).onBoard and ID == obj.ID and obj.Game.cardinPlay.race == "Secret"
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).discoverNew_MultiPools('', lambda : ShadowjewelerHanar.decidePools(kpr, kpr.Game.cardinPlay.Class))
		
	
class Trig_BoggspineKnuckles(TrigBoard):
	signals = ("HeroAttackedMinion", "HeroAttackedHero",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr.Game.heroes[kpr.ID] and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		func, ID = kpr.newEvolved, kpr.ID
		kpr.transform(minions := kpr.minionsonBoard(ID), [func(obj.mana_0, by=1, ID=ID) for obj in minions])
		
	
class Trig_Darkglare(TrigBoard):
	signals = ("HeroTookDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return ID == self.keeper.ID
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.restoreManaCrystal(1, kpr.ID)
		
	
class Trig_BulwarkofAzzinoth(TrigBoard):
	signals = ("FinalDmgonHero?",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return target is kpr.Game.heroes[kpr.ID] and kpr.onBoard and num[0] > 0
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		num[0] = 0
		self.keeper.losesDurability()
		
	
class Trig_KargathPrime(TrigBoard):
	signals = ("MinionAttackedMinion",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		kpr = self.keeper
		return subject is kpr and (target.health < 1 or target.dead) and kpr.onBoard
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).giveHeroAttackArmor(kpr.ID, armor=10)
		
	
class Trig_BloodboilBrute(TrigHand):
	signals = ("MinionAppears", "MinionDisappears", "MinionTakesDmg",)
	def canTrig(self, signal, ID, subject, target, num, comment, choice):
		return self.keeper.inHand
		
	def effect(self, signal, ID, subject, target, num, comment, choice):
		(kpr := self.keeper).Game.Manas.calcMana_Single(kpr)
		
	
class GameManaAura_KaelthasSunstrider(GameManaAura_OneTime):
	to = 1
	def __init__(self, Game, ID, keeper):
		super().__init__(Game, ID)
		self.keeper = keeper
		
	def applicable(self, target): return target.ID == self.ID and target.category == "Spell"
		
	def auraDisappears(self):
		super().auraDisappears()
		removefrom(self, self.keeper.auras)
		self.keeper.btn.effectChangeAni("Aura")
		
	def createCopy(self, game):
		if self not in game.copiedObjs:  # 这个光环没有被复制过
			game.copiedObjs[self] = auraCopy = type(self)(game, self.ID, self.keeper.createCopy(game))
			for receiver in self.receivers:
				auraCopy.receivers.append((receiverCopy := receiver.createCopy(game, auraCopy)))
				receiverCopy.recipient = receiver.recipient.createCopy(game)
			return auraCopy
		else: return game.copiedObjs[self]
		
	
class GameManaAura_AldorAttendant(GameManaAura_OneTime):
	signals, by, temporary = ("HandCheck",), -1, False
	def applicable(self, target): return target.ID == self.ID and "Libram of " in target.name
		
	
class GameManaAura_AldorTruthseeker(GameManaAura_OneTime):
	signals, by, temporary = ("HandCheck",), -2, False
	def applicable(self, target): return target.ID == self.ID and "Libram of " in target.name
		
	
class Minion_Dormantfor2turns(Minion):
	Class, race, name = "Neutral", "", "Imprisoned Vanilla"
	mana, attack, health = 5, 5, 5
	numTargets, Effects, description = 0, "", "Dormant for 2 turns. When this awakens, do something"
	index = "Uncollectible"
	def appears_fromPlay(self, choice):
		return super().appears(True, Trig_Imprisoned(self))
		
	def appears(self, firstTime=True, dormantTrig=None):
		return super().appears(firstTime, Trig_Imprisoned(self) if firstTime else None)
		
	def awakenEffect(self):
		pass
		
	
class EtherealAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Ethereal Augmerchant"
	mana, attack, health = 1, 2, 1
	name_CN = "虚灵改装师"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 1 damage to a minion and give it Spell Damage +1"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.dealsDamage(obj, 1)
			self.giveEnchant(obj, effGain="Spell Damage", source=EtherealAugmerchant)
		
	
class GuardianAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Guardian Augmerchant"
	mana, attack, health = 1, 2, 1
	name_CN = "防护改装师"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 1 damage to a minion and give it Divine Shield"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.dealsDamage(obj, 1)
			self.giveEnchant(obj, effGain="Divine Shield", source=GuardianAugmerchant)
		
	
class InfectiousSporeling(Minion):
	Class, race, name = "Neutral", "", "Infectious Sporeling"
	mana, attack, health = 1, 1, 2
	numTargets, Effects, description = 0, "", "After this damages a minion, turn it into an Infectious Sporeling"
	name_CN = "传染孢子"
	trigBoard = Trig_InfectiousSporeling		
	
	
class RocketAugmerchant(Minion):
	Class, race, name = "Neutral", "", "Rocket Augmerchant"
	mana, attack, health = 1, 2, 1
	name_CN = "火箭改装师"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 1 damage to a minion and give it Rush"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.dealsDamage(obj, 1)
			self.giveEnchant(obj, effGain="Rush", source=RocketAugmerchant)
		
	
class SoulboundAshtongue(Minion):
	Class, race, name = "Neutral", "", "Soulbound Ashtongue"
	mana, attack, health = 1, 1, 4
	numTargets, Effects, description = 0, "", "Whenever this minion takes damage, also deal that amount to your hero"
	name_CN = "魂缚灰舌"
	trigBoard = Trig_SoulboundAshtongue		
	
	
class BonechewerBrawler(Minion):
	Class, race, name = "Neutral", "", "Bonechewer Brawler"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "Taunt", "Taunt. Whenever this minion takes damage, gain +2 Attack"
	name_CN = "噬骨殴斗者"
	trigBoard = Trig_BonechewerBrawler
	
	
class ImprisonedVilefiend(Minion_Dormantfor2turns):
	Class, race, name = "Neutral", "Demon", "Imprisoned Vilefiend"
	mana, attack, health = 2, 3, 5
	numTargets, Effects, description = 0, "Rush", "Dormant for 2 turns. Rush"
	name_CN = "被禁锢的邪犬"
	
	
class MoargArtificer(Minion):
	Class, race, name = "Neutral", "Demon", "Mo'arg Artificer"
	mana, attack, health = 2, 2, 4
	numTargets, Effects, description = 0, "", "All minions take double damage from spells"
	name_CN = "莫尔葛工匠"
	trigBoard = Trig_MoargArtificer		
	
	
class RustswornInitiate(Minion):
	Class, race, name = "Neutral", "", "Rustsworn Initiate"
	mana, attack, health = 2, 2, 2
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 1/1 Impcaster with Spell Damage +1"
	name_CN = "锈誓新兵"
	deathrattle = Death_RustswornInitiate
	
	
class Impcaster(Minion):
	Class, race, name = "Neutral", "Demon", "Impcaster"
	mana, attack, health = 1, 1, 1
	name_CN = "小鬼施法者"
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage +1"
	index = "Uncollectible"
	
	
class BlisteringRot(Minion):
	Class, race, name = "Neutral", "", "Blistering Rot"
	mana, attack, health = 3, 1, 2
	numTargets, Effects, description = 0, "", "At the end of your turn, summon a Rot with stats equal to this minion's"
	name_CN = "起泡的腐泥怪"
	trigBoard = Trig_BlisteringRot		
	
	
class LivingRot(Minion):
	Class, race, name = "Neutral", "", "Living Rot"
	mana, attack, health = 1, 1, 1
	name_CN = "生命腐质"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class FrozenShadoweaver(Minion):
	Class, race, name = "Neutral", "", "Frozen Shadoweaver"
	mana, attack, health = 3, 4, 3
	name_CN = "冰霜织影者"
	numTargets, Effects, description = 1, "", "Battlecry: Freeze an enemy"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableCharExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category in ("Minion", "Hero") and obj.ID != self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.freeze(target)
		
	
class OverconfidentOrc(Minion):
	Class, race, name = "Neutral", "", "Overconfident Orc"
	mana, attack, health = 3, 1, 6
	numTargets, Effects, description = 0, "Taunt", "Taunt. While at full Health, this has +2 Attack"
	name_CN = "狂傲的兽人"
	def statCheckResponse(self):
		if self.onBoard and  not self.silenced and self.dmgTaken < 1: self.attack += 2
		
	
class TerrorguardEscapee(Minion):
	Class, race, name = "Neutral", "Demon", "Terrorguard Escapee"
	mana, attack, health = 3, 3, 7
	name_CN = "逃脱的恐惧卫士"
	numTargets, Effects, description = 0, "", "Battlecry: Summon three 1/1 Huntresses for your opponent"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([Huntress(self.Game, 3-self.ID) for _ in (0, 1, 2)], position=-1)
		
	
class Huntress(Minion):
	Class, race, name = "Neutral", "", "Huntress"
	mana, attack, health = 1, 1, 1
	name_CN = "女猎手"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class TeronGorefiend(Minion):
	Class, race, name = "Neutral", "", "Teron Gorefiend"
	mana, attack, health = 3, 3, 4
	name_CN = "塔隆血魔"
	numTargets, Effects, description = 0, "", "Battlecry: Destroy all friendly minions. Deathrattle: Resummon all of them with +1/+1"
	index = "Battlecry~Legendary"
	deathrattle = Death_TeronGorefiend
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#不知道两次触发战吼时亡语是否会记录两份，假设会
		if killed := self.Game.minionsonBoard(self.ID, exclude=self):
			self.Game.kill(self, killed)
			killed = [o.getBareInfo() for o in killed]
			for trig in self.deathrattles:
				if isinstance(trig, Death_TeronGorefiend):
					trig.memory += killed
		
	
class BurrowingScorpid(Minion):
	Class, race, name = "Neutral", "Beast", "Burrowing Scorpid"
	mana, attack, health = 4, 5, 2
	name_CN = "潜地蝎"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 2 damage. If that kills the target, gain Stealth"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.dealsDamage(obj, 2)
			if obj.health < 1 or obj.dead: self.giveEnchant(self, effGain="Stealth", source=BurrowingScorpid)
		
	
class DisguisedWanderer(Minion):
	Class, race, name = "Neutral", "Demon", "Disguised Wanderer"
	mana, attack, health = 4, 3, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 9/1 Inquisitor"
	name_CN = "变装游荡者"
	deathrattle = Death_DisguisedWanderer
	
	
class RustswornInquisitor(Minion):
	Class, race, name = "Neutral", "Demon", "Rustsworn Inquisitor"
	mana, attack, health = 4, 9, 1
	name_CN = "锈誓审判官"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class FelfinNavigator(Minion):
	Class, race, name = "Neutral", "Murloc", "Felfin Navigator"
	mana, attack, health = 4, 4, 4
	name_CN = "邪鳍导航员"
	numTargets, Effects, description = 0, "", "Battlecry: Give your other Murlocs +1/+1"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID, exclude=self, race="Murloc"), 1, 1, source=FelfinNavigator)
		
	
class Magtheridon(Minion):
	Class, race, name = "Neutral", "Demon", "Magtheridon"
	mana, attack, health = 4, 12, 12
	name_CN = "玛瑟里顿"
	numTargets, Effects, description = 0, "", "Dormant. Battlecry: Summon three 1/3 enemy Warders. When they die, destroy all minions and awaken"
	index = "Battlecry~Legendary"
	def appears_fromPlay(self, choice):
		return super().appears(True, Trig_Magtheridon(self))
		
	def appears(self, firstTime=True, dormantTrig=None):
		return super().appears(firstTime, Trig_Magtheridon(self) if firstTime else None)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.summon([HellfireWarder(self.Game, 3-self.ID) for _ in (0, 1, 2)], position=-1)
		
	
class HellfireWarder(Minion):
	Class, race, name = "Neutral", "", "Hellfire Warder"
	mana, attack, health = 1, 1, 3
	name_CN = "地狱火典狱官"
	numTargets, Effects, description = 0, "", "(Magtheridon will destroy all minions and awaken after 3 Warders die)"
	index = "Uncollectible"
	
	
class MaievShadowsong(Minion):
	Class, race, name = "Neutral", "", "Maiev Shadowsong"
	mana, attack, health = 4, 4, 3
	name_CN = "玛维影歌"
	numTargets, Effects, description = 1, "", "Battlecry: Choose a minion. It goes Dormant for 2 turns"
	index = "Battlecry~Legendary"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: #需要随从在场并且还是随从形态
			if obj.onBoard and obj.category == "Minion": obj.goDormant(Trig_Imprisoned(obj))
		
	
class Replicatotron(Minion):
	Class, race, name = "Neutral", "Mech", "Replicat-o-tron"
	mana, attack, health = 4, 3, 3
	numTargets, Effects, description = 0, "", "At the end of your turn, transform a neighbor into a copy of this"
	name_CN = "复制机器人"
	trigBoard = Trig_Replicatotron		
	
	
class RustswornCultist(Minion):
	Class, race, name = "Neutral", "", "Rustsworn Cultist"
	mana, attack, health = 4, 3, 3
	name_CN = "锈誓信徒"
	numTargets, Effects, description = 0, "", "Battlecry: Give your other minions 'Deathrattle: Summon a 1/1 Demon'"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), trig=Death_RustswornCultist, trigType="Deathrattle")
		
	
class RustedDevil(Minion):
	Class, race, name = "Neutral", "Demon", "Rusted Devil"
	mana, attack, health = 1, 1, 1
	name_CN = "铁锈恶鬼"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class Alar(Minion):
	Class, race, name = "Neutral", "Elemental", "Al'ar"
	mana, attack, health = 5, 7, 3
	name_CN = "奥"
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 0/3 Ashes of Al'ar that resurrects this minion on your next turn"
	index = "Legendary"
	deathrattle = Death_Alar
	
	
class AshesofAlar(Minion):
	Class, race, name = "Neutral", "", "Ashes of Al'ar"
	mana, attack, health = 1, 0, 3
	name_CN = "奥的灰烬”"
	numTargets, Effects, description = 0, "", "At the start of your turn, transform this into Al'ar"
	index = "Legendary~Uncollectible"
	trigBoard = Trig_AshesofAlar		
	
	
class RuststeedRaider(Minion):
	Class, race, name = "Neutral", "", "Ruststeed Raider"
	mana, attack, health = 5, 1, 8
	name_CN = "锈骑劫匪"
	numTargets, Effects, description = 0, "Taunt,Rush", "Taunt, Rush. Battlecry: Gain +4 Attack this turn"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self, statEnchant=Enchantment(RuststeedRaider, 4, 0, until=0))
		
	
class WasteWarden(Minion):
	Class, race, name = "Neutral", "", "Waste Warden"
	mana, attack, health = 5, 3, 3
	name_CN = "废土守望者"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 3 damage to a minion and all others of the same minion category"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.race and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#假设指定梦魇融合怪的时候会把场上所有有种族的随从都打一遍
		for obj in target:
			if obj.race == "": self.dealsDamage(obj, 3)
			else: #Minion has race
				minions = [obj] #不重复计算目标和对一个随从的伤害
				for race in obj.race.split(','): #A bunch of All category minions should be considered
					minions += [minion for minion in self.Game.minionsonBoard(race=race, exclude=obj) if minion not in minions]
				self.dealsDamage(minions, 3)
		
	
class DragonmawSkyStalker(Minion):
	Class, race, name = "Neutral", "Dragon", "Dragonmaw Sky Stalker"
	mana, attack, health = 6, 5, 6
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 3/4 Dragonrider"
	name_CN = "龙喉巡天者"
	deathrattle = Death_DragonmawSkyStalker
	
	
class Dragonrider(Minion):
	Class, race, name = "Neutral", "", "Dragonrider"
	mana, attack, health = 3, 3, 4
	name_CN = "龙骑士"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class KaelthasSunstrider(Minion):
	Class, race, name = "Neutral", "", "Kael'thas Sunstrider"
	mana, attack, health = 7, 4, 7
	name_CN = "凯尔萨斯·逐日者"
	numTargets, Effects, description = 0, "", "Every third spell you cast each turn costs (1)"
	index = "Legendary"
	trigBoard, trigEffect = Trig_KaelthasSunstrider, GameManaAura_KaelthasSunstrider
	
	
class ScavengingShivarra(Minion):
	Class, race, name = "Neutral", "Demon", "Scavenging Shivarra"
	mana, attack, health = 6, 6, 3
	name_CN = "食腐破坏魔"
	numTargets, Effects, description = 0, "", "Battlecry: Deal 6 damage randomly split among all other minions"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(6):
			if minions := self.Game.minionsAlive(exclude=self):
				self.dealsDamage(numpyChoice(minions), 1)
			else: break
		
	
class BonechewerVanguard(Minion):
	Class, race, name = "Neutral", "", "Bonechewer Vanguard"
	mana, attack, health = 7, 4, 10
	numTargets, Effects, description = 0, "Taunt", "Taunt. Whenever this minion takes damage, gain +2 Attack"
	name_CN = "噬骨先锋"
	trigBoard = Trig_BonechewerVanguard		
	
	
class SupremeAbyssal(Minion):
	Class, race, name = "Neutral", "Demon", "Supreme Abyssal"
	mana, attack, health = 8, 12, 12
	numTargets, Effects, description = 0, "Can't Attack Hero", "Can't attack heroes"
	name_CN = "深渊至尊"
	
	
class ScrapyardColossus(Minion):
	Class, race, name = "Neutral", "Elemental", "Scrapyard Colossus"
	mana, attack, health = 10, 7, 7
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Summon a 7/7 Felcracked Colossus with Taunt"
	name_CN = "废料场巨像"
	deathrattle = Death_ScrapyardColossus
	
	
class FelcrackedColossus(Minion):
	Class, race, name = "Neutral", "Elemental", "Felcracked Colossus"
	mana, attack, health = 7, 7, 7
	name_CN = "邪爆巨像"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class FuriousFelfin(Minion):
	Class, race, name = "Demon Hunter", "Murloc", "Furious Felfin"
	mana, attack, health = 2, 3, 2
	name_CN = "暴怒的邪鳍"
	numTargets, Effects, description = 0, "", "Battlecry: If your hero attacked this turn, gain +1 Attack and Rush"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examHeroAtks(self.ID, turnInd=self.Game.turnInd)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examHeroAtks(self.ID, turnInd=self.Game.turnInd):
			self.giveEnchant(self, 1, 0, effGain="Rush", source=FuriousFelfin)
		
	
class ImmolationAura(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Immolation Aura"
	numTargets, mana, Effects = 0, 2, ""
	description = "Deal 1 damage to all minions twice"
	name_CN = "献祭光环"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(1))
		self.Game.gathertheDead()
		self.dealsDamage(self.Game.minionsonBoard(), self.calcDamage(1))
		
	
class Netherwalker(Minion):
	Class, race, name = "Demon Hunter", "", "Netherwalker"
	mana, attack, health = 2, 2, 2
	name_CN = "虚无行者"
	numTargets, Effects, description = 0, "", "Battlecry: Discover a Demon"
	index = "Battlecry"
	poolIdentifier = "Demons as Demon Hunter"
	@classmethod
	def generatePool(cls, pools):
		return genPool_MinionsofRaceasClass(pools, "Demon")
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.discoverNew(comment, lambda : self.rngPool("Demons as "+class4Discover(self)))
		
	
class FelSummoner(Minion):
	Class, race, name = "Demon Hunter", "", "Fel Summoner"
	mana, attack, health = 6, 8, 3
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a random Demon from your hand"
	name_CN = "邪能召唤师"
	deathrattle = Death_FelSummoner
	
	
class KaynSunfury(Minion):
	Class, race, name = "Demon Hunter", "", "Kayn Sunfury"
	mana, attack, health = 4, 3, 4
	name_CN = "凯恩日怒"
	numTargets, Effects, description = 0, "Charge", "Charge. All friendly attacks ignore Taunt"
	index = "Legendary"
	aura = GameRuleAura_KaynSunfury
	
	
class Metamorphosis(Spell):
	Class, school, name = "Demon Hunter", "Fel", "Metamorphosis"
	numTargets, mana, Effects = 0, 5, ""
	name_CN = "恶魔变形"
	description = "Swap your Hero Power to 'Deal 4 damage'. After 2 uses, swap it back"
	index = "Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		DemonicBlast(self.Game, self.ID, self.Game.powers[self.ID]).replacePower()
		
	
class DemonicBlast(Power):
	mana, name, numTargets = 1, "Demonic Blast", 1
	description = "Deal 4 damage. (Two uses left!)"
	name_CN = "恶魔冲击"
	trigBoard = Trig_DemonicBlast
	def dealsDmg(self): return True
		
	def text(self): return self.calcDamage(4)
		
	def effect(self, target, choice=0):
		self.dealsDamage(target, self.calcDamage(4))
		
	
class ImprisonedAntaen(Minion_Dormantfor2turns):
	Class, race, name = "Demon Hunter", "Demon", "Imprisoned Antaen"
	mana, attack, health = 6, 10, 6
	numTargets, Effects, description = 0, "", "Dormant for 2 turns. When this awakens, deal 10 damage randomly split among all enemies"
	name_CN = "被禁锢的安塔恩"
	def awakenEffect(self):
		side = 3 - self.ID
		for _ in range(10):
			if objs := self.Game.charsAlive(side): self.dealsDamage(numpyChoice(objs), 1)
			else: break
		
	
class SkullofGuldan(Spell):
	Class, school, name = "Demon Hunter", "", "Skull of Gul'dan"
	numTargets, mana, Effects = 0, 6, ""
	description = "Draw 3 cards. Outscast: Reduce their Cost by (3)"
	name_CN = "古尔丹之颅"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.outcastcanTrig(self)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		outcastcanTrig = posinHand in (-1, 0)
		for _ in (0, 1, 2):
			card, mana, entersHand = self.Game.Hand_Deck.drawCard(self.ID)
			if outcastcanTrig and entersHand: ManaMod(card, by=-3).applies()
		
	
class PriestessofFury(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Priestess of Fury"
	mana, attack, health = 7, 6, 5
	numTargets, Effects, description = 0, "", "At the end of your turn, deal 6 damage randomly split among all enemies"
	name_CN = "愤怒的女祭司"
	trigBoard = Trig_PriestessofFury
	
	
class CoilfangWarlord(Minion):
	Class, race, name = "Demon Hunter", "", "Coilfang Warlord"
	mana, attack, health = 8, 9, 5
	numTargets, Effects, description = 0, "Rush", "Rush. Deathrattle: Summon a 5/9 Warlord with Taunt"
	name_CN = "盘牙督军"
	deathrattle = Death_CoilfangWarlord
	
	
class ConchguardWarlord(Minion):
	Class, race, name = "Demon Hunter", "", "Conchguard Warlord"
	mana, attack, health = 8, 5, 9
	name_CN = "螺盾督军"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class PitCommander(Minion):
	Class, race, name = "Demon Hunter", "Demon", "Pit Commander"
	mana, attack, health = 9, 7, 9
	numTargets, Effects, description = 0, "Taunt", "Taunt. At the end of your turn, summon a Demon from your deck"
	name_CN = "深渊指挥官"
	trigBoard = Trig_PitCommander		
	
	
class FungalFortunes(Spell):
	Class, school, name = "Druid", "Nature", "Fungal Fortunes"
	numTargets, mana, Effects = 0, 3, ""
	description = "Draw 3 cards. Discard any minions drawn"
	name_CN = "真菌宝藏"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#The minions will be discarded immediately after it entershand
		#The discarding triggers triggers["Discarded"] and send signals.
		#If the hand is full, then no discard at all. The drawn cards vanish.	
		#The "cast when drawn" spells can take effect as usual
		HD = self.Game.Hand_Deck
		ownDeck = HD.decks[self.ID]
		for _ in (0, 1, 2):
			if ownDeck:
				if ownDeck[-1].category == "Minion":
					HD.extractfromDeck(-1, self.ID)
				else: HD.drawCard(self.ID)
			else: break
		
	
class Ironbark(Spell):
	Class, school, name = "Druid", "Nature", "Ironbark"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a minion +1/+3 and Taunt. Costs (0) if you have at least 7 Mana Crystals"
	name_CN = "铁木树皮"
	trigHand = Trig_Ironbark		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def selfManaChange(self):
		#假设需要的是空水晶，暂时获得的水晶不算
		if self.Game.Manas.manasUpper[self.ID] > 6: self.mana = 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 1, 3, effGain="Taunt", source=Ironbark)
		
	
class ArchsporeMsshifn(Minion):
	Class, race, name = "Druid", "", "Archspore Msshi'fn"
	mana, attack, health = 3, 3, 4
	name_CN = "孢子首领姆希菲"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Shuffle 'Msshi'fn Prime' into your deck"
	index = "Legendary"
	deathrattle = Death_ArchsporeMsshifn
	
	
class MsshifnAttac_Option(Option):
	name, description = "Msshi'fn At'tac", "Summon a 9/9 with Taunt"
	mana, attack, health = 10, -1, -1
	isLegendary = True
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0
		
	
class MsshifnProtec_Option(Option):
	name, description = "Msshi'fn Pro'tec", "Summon a 9/9 with Rush"
	mana, attack, health = 10, -1, -1
	isLegendary = True
	def available(self):
		return self.keeper.Game.space(self.keeper.ID) > 0
		
	
class MsshifnPrime(Minion):
	Class, race, name = "Druid", "", "Msshi'fn Prime"
	mana, attack, health = 10, 9, 9
	name_CN = "终极姆希菲"
	numTargets, Effects, description = 0, "Taunt", "Taunt. Choose One- Summon a 9/9 Fungal Giant with Taunt; or Rush"
	index = "Legendary~Uncollectible"
	options = (MsshifnAttac_Option, MsshifnProtec_Option)
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#如果有全选光环，只有一个9/9，其同时拥有突袭和嘲讽
		if not choice: self.summon(FungalGuardian(self.Game, self.ID))
		elif choice == 1: self.summon(FungalBruiser(self.Game, self.ID))
		elif choice < 0: self.summon(FungalGargantuan(self.Game, self.ID))
		
	
class FungalGuardian(Minion):
	Class, race, name = "Druid", "", "Fungal Guardian"
	mana, attack, health = 10, 9, 9
	name_CN = "真菌守卫"
	numTargets, Effects, description = 0, "Taunt", "Taunt"
	index = "Uncollectible"
	
	
class FungalBruiser(Minion):
	Class, race, name = "Druid", "", "Fungal Bruiser"
	mana, attack, health = 10, 9, 9
	name_CN = "真菌打手"
	numTargets, Effects, description = 0, "Rush", "Rush"
	index = "Uncollectible"
	
	
class FungalGargantuan(Minion):
	Class, race, name = "Druid", "", "Fungal Gargantuan"
	mana, attack, health = 10, 9, 9
	name_CN = "真菌巨怪"
	numTargets, Effects, description = 0, "Taunt,Rush", "Taunt, Rush"
	index = "Uncollectible"
	
	
class Bogbeam(Spell):
	Class, school, name = "Druid", "", "Bogbeam"
	numTargets, mana, Effects = 1, 3, ""
	description = "Deal 3 damage to a minion. Costs (0) if you have at least 7 Mana Crystals"
	name_CN = "沼泽射线"
	trigHand = Trig_Bogbeam		
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def selfManaChange(self):
		#假设需要的是空水晶，暂时获得的水晶不算
		if self.Game.Manas.manasUpper[self.ID] > 6: self.mana = 0
		
	def effCanTrig(self):
		self.effectViable = self.Game.Manas.manasUpper[self.ID] > 6
		
	def text(self): return self.calcDamage(3)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		
	
class ImprisonedSatyr(Minion_Dormantfor2turns):
	Class, race, name = "Druid", "Demon", "Imprisoned Satyr"
	mana, attack, health = 3, 3, 3
	numTargets, Effects, description = 0, "", "Dormant for 2 turns. When this awakens, reduce the Cost of a random minion in your hand by (5)"
	name_CN = "被禁锢的萨特"
	def awakenEffect(self):
		if cards := self.findCards2ReduceMana(lambda card: card.category == "Minion"):
			ManaMod(numpyChoice(cards), by=-5).applies()
		
	
class Germination(Spell):
	Class, school, name = "Druid", "Nature", "Germination"
	numTargets, mana, Effects = 1, 4, ""
	description = "Summon a copy of a friendly minion. Give the copy Taunt"
	name_CN = "萌芽分裂"
	def available(self):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			Copy = self.summon(self.copyCard(obj, obj.ID), position=obj.pos+1)
			self.giveEnchant(Copy, effGain="Taunt", source=Germination)
		
	
class Overgrowth(Spell):
	Class, school, name = "Druid", "Nature", "Overgrowth"
	numTargets, mana, Effects = 0, 4, ""
	description = "Gain two empty Mana Crystals"
	name_CN = "过度生长"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.Game.Manas.gainEmptyManaCrystal(2, self.ID):
			self.addCardtoHand(ExcessMana, self.ID)
		
	
class GlowflySwarm(Spell):
	Class, school, name = "Druid", "", "Glowfly Swarm"
	numTargets, mana, Effects = 0, 5, ""
	description = "Summon a 2/2 Glowfly for each spell in your hand"
	name_CN = "萤火成群"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def effCanTrig(self):
		self.effectViable = any(card.category == "Spell" and card != self for card in self.Game.Hand_Deck.hands[self.ID])
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		num = sum(card.category == "Spell" for card in self.Game.Hand_Deck.hands[self.ID])
		if num > 0: self.summon([Glowfly(self.Game, self.ID) for i in range(num)])
		
	
class Glowfly(Minion):
	Class, race, name = "Druid", "Beast", "Glowfly"
	mana, attack, health = 2, 2, 2
	name_CN = "萤火虫"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class MarshHydra(Minion):
	Class, race, name = "Druid", "Beast", "Marsh Hydra"
	mana, attack, health = 7, 7, 7
	numTargets, Effects, description = 0, "Rush", "Rush. After this attacks, add a random 8-Cost minion to your hand"
	name_CN = "沼泽多头蛇"
	trigBoard = Trig_MarshHydra
	poolIdentifier = "8-Cost Minions"
	@classmethod
	def generatePool(cls, pools):
		return "8-Cost Minions", pools.MinionsofCost[8]
		
	
class YsielWindsinger(Minion):
	Class, race, name = "Druid", "", "Ysiel Windsinger"
	mana, attack, health = 9, 5, 5
	name_CN = "伊谢尔风歌"
	numTargets, Effects, description = 0, "", "Your spells cost (1)"
	index = "Legendary"
	aura = ManaAura_YsielWindsinger
	
	
class Helboar(Minion):
	Class, race, name = "Hunter", "Beast", "Helboar"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Give a random Beast in your hand +1/+1"
	name_CN = "地狱野猪"
	deathrattle = Death_Helboar
	
	
class ImprisonedFelmaw(Minion_Dormantfor2turns):
	Class, race, name = "Hunter", "Demon", "Imprisoned Felmaw"
	mana, attack, health = 2, 5, 4
	numTargets, Effects, description = 0, "", "Dormant for 2 turns. When this awakens, attack a random enemy"
	name_CN = "被禁锢的魔喉"
	def awakenEffect(self):
		if objs := self.Game.charsAlive(3-self.ID): self.Game.battle(self, numpyChoice(objs))
		
	
class PackTactics(Secret):
	Class, school, name = "Hunter", "", "Pack Tactics"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: When a friendly minion is attacked, summon a 3/3 copy"
	name_CN = "集群战术"
	trigBoard = Trig_PackTactics
	num = 1
	
	
class ScavengersIngenuity(Spell):
	Class, school, name = "Hunter", "", "Scavenger's Ingenuity"
	numTargets, mana, Effects = 0, 2, ""
	description = "Draw a Beast. Give it +2/+2"
	name_CN = "拾荒者的智慧"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		beast, mana, entersHand = self.drawCertainCard(lambda card: "Beast" in card.race)
		if entersHand: self.giveEnchant(beast, 2, 2, source=ScavengersIngenuity, add2EventinGUI=False)
		
	
class AugmentedPorcupine(Minion):
	Class, race, name = "Hunter", "Beast", "Augmented Porcupine"
	mana, attack, health = 3, 2, 4
	numTargets, Effects, description = 0, "", "Deathrattle: Deals this minion's Attack damage randomly split among all enemies"
	name_CN = "强能箭猪"
	deathrattle = Death_AugmentedPorcupine
	
	
class ZixorApexPredator(Minion):
	Class, race, name = "Hunter", "Beast", "Zixor, Apex Predator"
	mana, attack, health = 3, 2, 4
	name_CN = "顶级捕食者兹克索尔"
	numTargets, Effects, description = 0, "Rush", "Rush. Deathrattle: Shuffle 'Zixor Prime' into your deck"
	index = "Legendary"
	deathrattle = Death_ZixorApexPredator
	
	
class ZixorPrime(Minion):
	Class, race, name = "Hunter", "Beast", "Zixor Prime"
	mana, attack, health = 8, 4, 4
	name_CN = "终极兹克索尔"
	numTargets, Effects, description = 0, "Rush", "Rush. Battlecry: Summon 3 copies of this minion"
	index = "Battlecry~Legendary~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if not self.dead: self.summon([self.copyCard(self, self.ID) for _ in (0, 1, 2)])
		
	
class MokNathalLion(Minion):
	Class, race, name = "Hunter", "Beast", "Mok'Nathal Lion"
	mana, attack, health = 4, 5, 2
	name_CN = "莫克纳萨将狮"
	numTargets, Effects, description = 1, "Rush", "Rush. Battlecry: Choose a friendly minion. Gain a copy of its Deathrattle"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.targetExists()
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID == self.ID and obj is not self and obj.onBoard and obj.deathrattles
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			for trig in obj.deathrattles: self.getsTrig(trig.selfCopy(self), trigType="Deathrattle")
		
	
class ScrapShot(Spell):
	Class, school, name = "Hunter", "", "Scrap Shot"
	numTargets, mana, Effects = 1, 4, ""
	description = "Deal 3 damage. Give a random Beast in your hand +3/+3"
	name_CN = "废铁射击"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		if beasts := [card for card in self.Game.Hand_Deck.hands[self.ID] if "Beast" in card.race]:
			self.giveEnchant(numpyChoice(beasts), 3, 3, source=ScrapShot, add2EventinGUI=False)
		
	
class BeastmasterLeoroxx(Minion):
	Class, race, name = "Hunter", "", "Beastmaster Leoroxx"
	mana, attack, health = 8, 5, 5
	name_CN = "兽王莱欧洛克斯"
	numTargets, Effects, description = 0, "", "Battlecry: Summon 3 Beasts from your hand"
	index = "Battlecry~Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		refMinion = self
		for _ in (0, 1, 2):
			if not (refMinion := self.try_SummonfromOwn(refMinion.pos+1, hand_deck=0, cond=lambda card: "Beast" in card.race)): break
		
	
class NagrandSlam(Spell):
	Class, school, name = "Hunter", "", "Nagrand Slam"
	numTargets, mana, Effects = 0, 10, ""
	description = "Summon four 3/5 Clefthoofs that attack random enemies"
	name_CN = "纳格兰大冲撞"
	def available(self):
		return self.Game.space(self.ID) > 0
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		clefthoofs = [Clefthoof(game, self.ID) for _ in (0, 1, 2, 3)]
		self.summon(clefthoofs)
		for clefthoof in clefthoofs:
			if clefthoof.canBattle():
				if objs := game.charsAlive(3-self.ID): game.battle(clefthoof, numpyChoice(objs))
				else: break
		
	
class Clefthoof(Minion):
	Class, race, name = "Hunter", "Beast", "Clefthoof"
	mana, attack, health = 4, 3, 5
	name_CN = "裂蹄牛"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class Evocation(Spell):
	Class, school, name = "Mage", "Arcane", "Evocation"
	numTargets, mana, Effects = 0, 2, ""
	name_CN = "唤醒"
	description = "Fill your hand with random Mage spells. At the end of your turn, discard them"
	index = "Legendary"
	trigEffect = Trig_Evocation
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		curGame = self.Game
		pool = tuple(self.rngPool("Mage Spells"))
		while curGame.Hand_Deck.handNotFull(self.ID):
			spell = numpyChoice(pool)(curGame, self.ID)
			spell.trigsHand.append(Trig_Evocation(spell))
			self.addCardtoHand(spell, self.ID)
		
	
class FontofPower(Spell):
	Class, school, name = "Mage", "Arcane", "Font of Power"
	numTargets, mana, Effects = 0, 1, ""
	description = "Discover a Mage minion. If your deck has no minions, keep all 3"
	name_CN = "能量之泉"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noMinionsinDeck(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		poolFunc = lambda : self.rngPool("Mage Minions")
		if self.Game.Hand_Deck.noMinionsinDeck(self.ID):
			self.addCardtoHand(numpyChoice(poolFunc(), 3, replace=False), self.ID, byDiscover=True)
		else: self.discoverNew(comment, poolFunc)
		
	
class ApexisSmuggler(Minion):
	Class, race, name = "Mage", "", "Apexis Smuggler"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "After you play a Secret, Discover a spell"
	name_CN = "埃匹希斯走私犯"
	trigBoard = Trig_ApexisSmuggler
	
	
class AstromancerSolarian(Minion):
	Class, race, name = "Mage", "", "Astromancer Solarian"
	mana, attack, health = 2, 3, 2
	name_CN = "星术师索兰莉安"
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage +1. Deathrattle: Shuffle 'Solarian Prime' into your deck"
	index = "Legendary"
	deathrattle = Death_AstromancerSolarian
	
	
class SolarianPrime(Minion):
	Class, race, name = "Mage", "Demon", "Solarian Prime"
	mana, attack, health = 9, 7, 7
	name_CN = "终极索兰莉安"
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage +1. Battlecry: Cast 5 random Mage spells (target enemies if possible)"
	index = "Battlecry~Legendary~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(5):
			numpyChoice(self.rngPool("Mage Spells"))(self.Game, self.ID).cast(prefered=lambda obj: obj.ID != self.ID)
			self.Game.gathertheDead(decideWinner=True)
		
	
class IncantersFlow(Spell):
	Class, school, name = "Mage", "Arcane", "Incanter's Flow"
	numTargets, mana, Effects = 0, 3, ""
	description = "Reduce the Cost of spells in your deck by (1)"
	name_CN = "咒术洪流"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for card in self.Game.Hand_Deck.decks[self.ID][:]:
			if card.category == "Spell": ManaMod(card, by=-1).applies()
		
	
class Starscryer(Minion):
	Class, race, name = "Mage", "", "Starscryer"
	mana, attack, health = 2, 3, 1
	numTargets, Effects, description = 0, "", "Deathrattle: Draw a spell"
	name_CN = "星占师"
	deathrattle = Death_Starscryer
	
	
class ImprisonedObserver(Minion_Dormantfor2turns):
	Class, race, name = "Mage", "Demon", "Imprisoned Observer"
	mana, attack, health = 3, 4, 5
	numTargets, Effects, description = 0, "", "Dormant for 2 turns. When this awakens, deal 2 damage to all enemy minions"
	name_CN = "被禁锢的眼魔"
	def awakenEffect(self):
		self.dealsDamage(self.Game.minionsonBoard(3-self.ID), 2)
		
	
class NetherwindPortal(Secret):
	Class, school, name = "Mage", "Arcane", "Netherwind Portal"
	numTargets, mana, Effects = 0, 3, ""
	description = "Secret: After your opponent casts a spell, summon a random 4-Cost minion"
	name_CN = "虚空之风传送门"
	trigBoard = Trig_NetherwindPortal
	
	
class ApexisBlast(Spell):
	Class, school, name = "Mage", "", "Apexis Blast"
	numTargets, mana, Effects = 1, 5, ""
	description = "Deal 5 damage. If your deck has no minions, summon a random 5-Cost minion"
	name_CN = "埃匹希斯冲击"
	def effCanTrig(self):
		self.effectViable = self.Game.Hand_Deck.noMinionsinDeck(self.ID)
		
	def text(self): return self.calcDamage(5)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(5))
		if self.Game.Hand_Deck.noMinionsinDeck(self.ID):
			self.summon(numpyChoice(self.rngPool("5-Cost Minions to Summon"))(self.Game, self.ID))
		
	
class DeepFreeze(Spell):
	Class, school, name = "Mage", "Frost", "Deep Freeze"
	numTargets, mana, Effects = 1, 8, ""
	description = "Freeze an enemy. Summon two 3/6 Water Elementals"
	name_CN = "深度冻结"
	def available(self):
		return self.selectableCharExists(3 - self.ID)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category in ("Minion", "Hero") and obj.ID != self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.freeze(target)
		self.summon([WaterElemental(self.Game, self.ID) for _ in (0, 1)])
		
	
class ImprisonedSungill(Minion_Dormantfor2turns):
	Class, race, name = "Paladin", "Murloc", "Imprisoned Sungill"
	mana, attack, health = 1, 2, 1
	numTargets, Effects, description = 0, "", "Dormant for 2 turns. When this awakens, Summon two 1/1 Murlocs"
	name_CN = "被禁锢的阳鳃鱼人"
	def awakenEffect(self):
		self.summon([SungillStreamrunner(self.Game, self.ID) for _ in (0, 1)], relative="<>")
		
	
class SungillStreamrunner(Minion):
	Class, race, name = "Paladin", "Murloc", "Sungill Streamrunner"
	mana, attack, health = 1, 1, 1
	name_CN = "阳鳃士兵"
	numTargets, Effects, description = 0, "", ""
	index = "Uncollectible"
	
	
class AldorAttendant(Minion):
	Class, race, name = "Paladin", "", "Aldor Attendant"
	mana, attack, health = 1, 1, 3
	name_CN = "奥尔多侍从"
	numTargets, Effects, description = 0, "", "Battlecry: Reduce the Cost of your Librams by (1) this game"
	index = "Battlecry"
	trigEffect = GameManaAura_AldorAttendant
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_AldorAttendant(self.Game, self.ID).auraAppears()
		
	
class HandofAdal(Spell):
	Class, school, name = "Paladin", "Holy",  "Hand of A'dal"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a minion +2/+1. Draw a card"
	name_CN = "阿达尔之手"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 1, source=HandofAdal)
		self.Game.Hand_Deck.drawCard(self.ID)
		
	
class MurgurMurgurgle(Minion):
	Class, race, name = "Paladin", "Murloc", "Murgur Murgurgle"
	mana, attack, health = 2, 2, 1
	name_CN = "莫戈尔·莫戈尔格"
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield. Deathrattle: Shuffle 'Murgurgle Prime' into your deck"
	index = "Legendary"
	deathrattle = Death_MurgurMurgurgle
	
	
class MurgurglePrime(Minion):
	Class, race, name = "Paladin", "Murloc", "Murgurgle Prime"
	mana, attack, health = 8, 6, 3
	name_CN = "终极莫戈尔格"
	numTargets, Effects, description = 0, "Divine Shield", "Divine Shield. Battlecry: Summon 4 random Murlocs. Give them Divine Shield"
	index = "Battlecry~Legendary~Uncollectible"
	poolIdentifier = "Murlocs to Summon"
	@classmethod
	def generatePool(cls, pools):
		return "Murlocs to Summon", pools.MinionswithRace["Murloc"]
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		murlocs = [murloc(self.Game, self.ID) for murloc in numpyChoice(self.rngPool("Murlocs to Summon"), 4, replace=True)]
		self.summon(murlocs, relative="<>")
		self.giveEnchant(murlocs, effGain="Divine Shield", source=MurgurglePrime)
		
	
class LibramofWisdom(Spell):
	Class, school, name = "Paladin", "Holy",  "Libram of Wisdom"
	numTargets, mana, Effects = 1, 2, ""
	description = "Give a minion +1/+1 and 'Deathrattle: Add a 'Libram of Wisdom' spell to your hand'"
	name_CN = "智慧圣契"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 1, 1, source=LibramofWisdom, trig=Death_LibramofWisdom, trigType="Deathrattle")
		
	
class UnderlightAnglingRod(Weapon):
	Class, name, description = "Paladin", "Underlight Angling Rod", "After your hero attacks, add a random Murloc to your hand"
	mana, attack, durability, Effects = 3, 3, 2, ""
	name_CN = "幽光鱼竿"
	trigBoard = Trig_UnderlightAnglingRod
	
	
class AldorTruthseeker(Minion):
	Class, race, name = "Paladin", "", "Aldor Truthseeker"
	mana, attack, health = 5, 4, 6
	name_CN = "奥尔多真理追寻者"
	numTargets, Effects, description = 0, "", "Battlecry: Reduce the Cost of your Librams by (2) this game"
	index = "Battlecry"
	trigEffect = GameManaAura_AldorTruthseeker
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		GameManaAura_AldorTruthseeker(self.Game, self.ID).auraAppears()
		
	
class LibramofJustice(Spell):
	Class, school, name = "Paladin", "Holy",  "Libram of Justice"
	numTargets, mana, Effects = 0, 5, ""
	description = "Equip a 1/4 weapon. Change the Health of all enemy minions to 1"
	name_CN = "正义圣契"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.equipWeapon(OverdueJustice(self.Game, self.ID))
		self.setStat(self.Game.minionsonBoard(3 - self.ID), (None, 1), source=LibramofJustice)
		
	
class OverdueJustice(Weapon):
	Class, name, description = "Paladin", "Overdue Justice", ""
	mana, attack, durability, Effects = 1, 1, 4, ""
	name_CN = "迟到的正义"
	index = "Uncollectible"
	
	
class LadyLiadrin(Minion):
	Class, race, name = "Paladin", "", "Lady Liadrin"
	mana, attack, health = 7, 4, 6
	name_CN = "女伯爵莉亚德琳"
	numTargets, Effects, description = 0, "", "Battlecry: Add a copy of each spell you cast on friendly characters this game to your hand"
	index = "Battlecry~Legendary"
	def text(self):
		return self.Game.Counters.examCardPlays(self.ID, veri_sum_ls=1, cond=lambda tup: self.Game.Counters.checkTup_SpellonFriendly(tup, self.ID))
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game = self.Game
		if (n := game.Hand_Deck.spaceinHand(self.ID)) > 0 and (tups := list(game.Counters.iter_SpellsonFriendly(self.ID))):
			tups = numpyChoice(tups, min(n, len(tups)), replace=False)
			self.addCardtoHand([game.fabCard(tup, self.ID, self) for tup in tups], self.ID)
		
	
class LibramofHope(Spell):
	Class, school, name = "Paladin", "Holy", "Libram of Hope"
	numTargets, mana, Effects = 1, 9, ""
	description = "Restore 8 Health. Summon an 8/8 with Guardian with Taunt and Divine Shield"
	name_CN = "希望圣契"
	def text(self): return self.calcHeal(8)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(8))
		self.summon(AncientGuardian(self.Game, self.ID))
		
	
class AncientGuardian(Minion):
	Class, race, name = "Paladin", "", "Ancient Guardian"
	mana, attack, health = 8, 8, 8
	name_CN = "远古守卫"
	numTargets, Effects, description = 0, "Taunt,Divine Shield", "Taunt, Divine Shield"
	index = "Uncollectible"
	
	
class ImprisonedHomunculus(Minion_Dormantfor2turns):
	Class, race, name = "Priest", "Demon", "Imprisoned Homunculus"
	mana, attack, health = 1, 2, 5
	numTargets, Effects, description = 0, "Taunt", "Dormant for 2 turns. Taunt"
	name_CN = "被禁锢的矮劣魔"
	
	
class ReliquaryofSouls(Minion):
	Class, race, name = "Priest", "", "Reliquary of Souls"
	mana, attack, health = 1, 1, 3
	name_CN = "灵魂之匣"
	numTargets, Effects, description = 0, "Lifesteal", "Lifesteal. Deathrattle: Shuffle 'Leliquary Prime' into your deck"
	index = "Legendary"
	deathrattle = Death_ReliquaryofSouls
	
	
class ReliquaryPrime(Minion):
	Class, race, name = "Priest", "", "Reliquary Prime"
	mana, attack, health = 7, 6, 8
	name_CN = "终极魂匣"
	numTargets, Effects, description = 0, "Taunt,Lifesteal,Enemy Evasive", "Taunt, Lifesteal. Only you can target this with spells and Hero Powers"
	index = "Legendary~Uncollectible"
	
	
class Renew(Spell):
	Class, school, name = "Priest", "Holy", "Renew"
	numTargets, mana, Effects = 1, 1, ""
	description = "Restore 3 Health. Discover a spell"
	name_CN = "复苏"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.heals(target, self.calcHeal(3))
		self.discoverNew(comment, lambda : self.rngPool(class4Discover(self)+" Spells"))
		
	
class DragonmawSentinel(Minion):
	Class, race, name = "Priest", "", "Dragonmaw Sentinel"
	mana, attack, health = 2, 1, 4
	name_CN = "龙喉哨兵"
	numTargets, Effects, description = 0, "", "Battlecry: If you're holding a Dragon, gain +1 Attack and Lifesteal"
	index = "Battlecry"
	def effCanTrig(self): #Friendly characters are always selectable.
		self.effectViable = self.Game.Hand_Deck.holdingDragon(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Hand_Deck.holdingDragon(self.ID):
			self.giveEnchant(self, 1, 0, effGain="Lifesteal", source=DragonmawSentinel)
		
	
class SethekkVeilweaver(Minion):
	Class, race, name = "Priest", "", "Sethekk Veilweaver"
	mana, attack, health = 2, 2, 3
	numTargets, Effects, description = 0, "", "After you cast a spell on a minion, add a Priest spell to your hand"
	name_CN = "塞泰克织巢者"
	trigBoard = Trig_SethekkVeilweaver
	
	
class Apotheosis(Spell):
	Class, school, name = "Priest", "Holy", "Apotheosis"
	numTargets, mana, Effects = 1, 3, ""
	description = "Give a minion +2/+3 and Lifesteal"
	name_CN = "神圣化身"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, 2, 3, effGain="Lifesteal", source=Apotheosis)
		
	
class DragonmawOverseer(Minion):
	Class, race, name = "Priest", "", "Dragonmaw Overseer"
	mana, attack, health = 3, 2, 2
	numTargets, Effects, description = 0, "", "At the end of your turn, give another friendly minion +2/+2"
	name_CN = "龙喉监工"
	trigBoard = Trig_DragonmawOverseer		
	
	
class PsycheSplit(Spell):
	Class, school, name = "Priest", "Shadow", "Psyche Split"
	numTargets, mana, Effects = 1, 5, ""
	description = "Give a minion +1/+2. Summon a copy of it"
	name_CN = "心灵分裂"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.giveEnchant(obj, 1, 2, source=PsycheSplit)
			self.summon(self.copyCard(obj, obj.ID), position=obj.pos+1)
		
	
class SkeletalDragon(Minion):
	Class, race, name = "Priest", "Dragon", "Skeletal Dragon"
	mana, attack, health = 7, 4, 9
	numTargets, Effects, description = 0, "Taunt", "Taunt. At the end of your turn, add a Dragon to your hand"
	name_CN = "骸骨巨龙"
	trigBoard = Trig_SkeletalDragon
	
	
class SoulMirror(Spell):
	Class, school, name = "Priest", "Shadow", "Soul Mirror"
	numTargets, mana, Effects = 0, 7, ""
	name_CN = "灵魂之镜"
	description = "Summon copies of enemy minions. They attack their copies"
	index = "Legendary"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.minionsonBoard(3-self.ID):
			pairs = [minions, [self.copyCard(minion, self.ID) for minion in minions]]
			if self.summon(pairs[1]):
				for minion, Copy in zip(pairs[0], pairs[1]):
					if minion.canBattle() and Copy.canBattle(): self.Game.battle(Copy, minion)
		
	
class BlackjackStunner(Minion):
	Class, race, name = "Rogue", "", "Blackjack Stunner"
	mana, attack, health = 1, 1, 2
	name_CN = "钉棍终结者"
	numTargets, Effects, description = 1, "", "Battlecry: If you control a Secret, return a minion to its owner's hand. It costs (1) more"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = self.Game.Secrets.secrets[self.ID]
		
	def numTargetsNeeded(self, choice=0):
		return 1 if self.Game.Secrets.secrets[self.ID] else 0
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: self.Game.returnObj2Hand(self, obj, manaMod=ManaMod(obj, by=+1))
		
	
class Spymistress(Minion):
	Class, race, name = "Rogue", "", "Spymistress"
	mana, attack, health = 1, 3, 1
	numTargets, Effects, description = 0, "Stealth", "Stealth"
	name_CN = "间谍女郎"
	
	
class Ambush(Secret):
	Class, school, name = "Rogue", "", "Ambush"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: After your opponent plays a minion, summon a 2/3 Ambusher with Poisonous"
	name_CN = "伏击"
	trigBoard = Trig_Ambush
	
	
class BrokenAmbusher(Minion):
	Class, race, name = "Rogue", "", "Broken Ambusher"
	mana, attack, health = 2, 2, 3
	name_CN = "破碎者伏兵"
	numTargets, Effects, description = 0, "Poisonous", "Poisonous"
	index = "Uncollectible"
	
	
class AshtongueSlayer(Minion):
	Class, race, name = "Rogue", "", "Ashtongue Slayer"
	mana, attack, health = 2, 3, 2
	name_CN = "灰舌杀手"
	numTargets, Effects, description = 1, "", "Battlecry: Give a Stealthed minion +3 Attack and Immune this turn"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(self.ID, choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and (obj.effects["Stealth"] > 0 or obj.effects["Temp Stealth"] > 0) and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(target, statEnchant=Enchantment(AshtongueSlayer, 3, 0, until=0),
								effectEnchant=Enchantment(AshtongueSlayer, effGain="Immune", until=0))
		
	
class Bamboozle(Secret):
	Class, school, name = "Rogue", "", "Bamboozle"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: When one of your minions is attacked, transform it into a random one that costs (3) more"
	name_CN = "偷天换日"
	trigBoard = Trig_Bamboozle
	
	
class DirtyTricks(Secret):
	Class, school, name = "Rogue", "", "Dirty Tricks"
	numTargets, mana, Effects = 0, 2, ""
	description = "Secret: After your opponent casts a spell, draw 2 cards"
	name_CN = "邪恶计谋"
	trigBoard = Trig_DirtyTricks
	
	
class ShadowjewelerHanar(Minion):
	Class, race, name = "Rogue", "", "Shadowjeweler Hanar"
	mana, attack, health = 2, 1, 4
	name_CN = "暗影珠宝师汉纳尔"
	numTargets, Effects, description = 0, "", "After you play a Secret, Discover a Secret from a different class"
	index = "Legendary"
	trigBoard = Trig_ShadowjewelerHanar
	def decidePools(self, Class2Exclude):
		classes = (Class for Class in ("Hunter", "Mage", "Paladin", "Rogue") if Class != Class2Exclude)
		return [self.rngPool(Class + " Secrets") for Class in classes]
		
	
class Akama(Minion):
	Class, race, name = "Rogue", "", "Akama"
	mana, attack, health = 3, 3, 4
	name_CN = "阿卡玛"
	numTargets, Effects, description = 0, "Stealth", "Stealth. Deathrattle: Shuffle 'Akama Prime' into your deck"
	index = "Legendary"
	deathrattle = Death_Akama
	
	
class AkamaPrime(Minion):
	Class, race, name = "Rogue", "", "Akama Prime"
	mana, attack, health = 6, 6, 5
	name_CN = "终极阿卡玛"
	numTargets, Effects, description = 0, "Stealth", "Permanently Stealthed"
	index = "Legendary~Uncollectible"
	def losesEffect(self, effect, amount=1, removeEnchant=False, loseAllEffects=False):
		if effect != "Stealth" or self.silenced:
			super().losesEffect(effect, amount)
		
	
class GreyheartSage(Minion):
	Class, race, name = "Rogue", "", "Greyheart Sage"
	mana, attack, health = 3, 3, 3
	name_CN = "暗心贤者"
	numTargets, Effects, description = 0, "", "Battlecry: If you control a Stealth minion, draw 2 cards"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.effects["Stealth"] > 0 or minion.effects["Temp Stealth"] > 0:
				self.effectViable = True
				break
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		controlStealthMinion = False
		for minion in self.Game.minionsonBoard(self.ID):
			if minion.effects["Stealth"] > 0 or minion.effects["Temp Stealth"] > 0:
				controlStealthMinion = True
				break
		if controlStealthMinion:
			self.Game.Hand_Deck.drawCard(self.ID)
			self.Game.Hand_Deck.drawCard(self.ID)
		
	
class CursedVagrant(Minion):
	Class, race, name = "Rogue", "", "Cursed Vagrant"
	mana, attack, health = 7, 7, 5
	numTargets, Effects, description = 0, "", "Deathrattle: Summon a 7/5 Shadow with Stealth"
	name_CN = "被诅咒的 流浪者"
	deathrattle = Death_CursedVagrant
	
	
class CursedShadow(Minion):
	Class, race, name = "Rogue", "", "Cursed Shadow"
	mana, attack, health = 7, 7, 5
	name_CN = "被诅咒的阴影"
	numTargets, Effects, description = 0, "Stealth", "Stealth"
	index = "Uncollectible"
	
	
class BogstrokClacker(Minion):
	Class, race, name = "Shaman", "", "Bogstrok Clacker"
	mana, attack, health = 3, 3, 3
	name_CN = "泥泽巨拳龙虾人"
	numTargets, Effects, description = 0, "", "Battlecry: Transform adjacent minions into random minions that cost (1) more"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if minions := self.Game.neighbors2(self)[0]:
			self.transform(minions, [self.newEvolved(obj.mana_0, by=1, ID=self.ID) for obj in minions])
		
	
class LadyVashj(Minion):
	Class, race, name = "Shaman", "", "Lady Vashj"
	mana, attack, health = 3, 4, 3
	name_CN = "瓦斯琪女士"
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage +1. Deathrattle: Shuffle 'Vashj Prime' into your deck"
	index = "Legendary"
	deathrattle = Death_LadyVashj
	
	
class VashjPrime(Minion):
	Class, race, name = "Shaman", "", "Vashj Prime"
	mana, attack, health = 7, 5, 4
	name_CN = "终极瓦斯琪"
	numTargets, Effects, description = 0, "Spell Damage", "Spell Damage +1. Battlecry: Draw 3 spells. Reduce their Cost by (3)"
	index = "Battlecry~Legendary~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2):
			spell, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Spell")
			if not spell: break
			elif entersHand: ManaMod(spell, by=-3).applies()
		
	
class Marshspawn(Minion):
	Class, race, name = "Shaman", "Elemental", "Marshspawn"
	mana, attack, health = 3, 3, 4
	name_CN = "沼泽之子"
	numTargets, Effects, description = 0, "", "Battlecry: If you cast a spell last turn, Discover a spell"
	index = "Battlecry"
	def effCanTrig(self):
		cardsEachTurn = self.Game.Counters.examSpellsLastTurn(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examSpellsLastTurn(self.ID):
			self.discoverNew(comment, lambda : self.rngPool(class4Discover(self)+" Spells"))
		
	
class SerpentshrinePortal(Spell):
	Class, school, name = "Shaman", "Nature", "Serpentshrine Portal"
	numTargets, mana, Effects = 1, 3, ""
	description = "Deal 3 damage. Summon a random 3-Cost minion. Overload: (1)"
	name_CN = "毒蛇神殿传送门"
	overload = 1
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(3))
		self.summon(numpyChoice(self.rngPool("3-Cost Minions to Summon"))(self.Game, self.ID))
		
	
class TotemicReflection(Spell):
	Class, school, name = "Shaman", "", "Totemic Reflection"
	numTargets, mana, Effects = 1, 3, ""
	description = "Give a minion +2/2. If it's a Totem, summon a copy of it"
	name_CN = "图腾映像"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target:
			self.giveEnchant(obj, 2, 2, source=TotemicReflection)
			if "Totem" in obj.race: self.summon(self.copyCard(obj, obj.ID), position=obj.pos+1)
		
	
class Torrent(Spell):
	Class, school, name = "Shaman", "Nature", "Torrent"
	numTargets, mana, Effects = 1, 4, ""
	description = "Deal 8 damage to a minion. Costs (3) less if you cast a spell last turn"
	name_CN = "洪流"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.Game.Counters.examSpellsLastTurn(self.ID)
		
	def selfManaChange(self):
		if self.Game.Counters.examSpellsLastTurn(self.ID): self.mana -= 3
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(8))
		
	
class VividSpores(Spell):
	Class, school, name = "Shaman", "Nature", "Vivid Spores"
	numTargets, mana, Effects = 0, 4, ""
	description = "Give your minions 'Deathrattle: Resummon this minion'"
	name_CN = "鲜活孢子"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.giveEnchant(self.Game.minionsonBoard(self.ID), trig=Death_VividSpores, trigType="Deathrattle")
		
	
class BoggspineKnuckles(Weapon):
	Class, name, description = "Shaman", "Boggspine Knuckles", "After your hero attacks, transform your minions into ones that cost (1) more"
	mana, attack, durability, Effects = 5, 3, 2, ""
	name_CN = "沼泽拳刺"
	trigBoard = Trig_BoggspineKnuckles
	
	
class ShatteredRumbler(Minion):
	Class, race, name = "Shaman", "Elemental", "Shattered Rumbler"
	mana, attack, health = 5, 5, 6
	name_CN = "破碎奔行者"
	numTargets, Effects, description = 0, "", "Battlecry: If you cast a spell last turn, deal 2 damage to all other minions"
	index = "Battlecry"
	def effCanTrig(self):
		cardsEachTurn = self.Game.Counters.examSpellsLastTurn(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.Game.Counters.examSpellsLastTurn(self.ID):
			self.dealsDamage(self.Game.minionsonBoard(exclude=self), 2)
		
	
class TheLurkerBelow(Minion):
	Class, race, name = "Shaman", "Beast", "The Lurker Below"
	mana, attack, health = 6, 6, 5
	name_CN = "鱼斯拉"
	numTargets, Effects, description = 1, "", "Battlecry: Deal 3 damage to an enemy minion, it dies, repeat on one of its neighbors"
	index = "Battlecry~Legendary"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(3 - self.ID, choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		#假设战吼触发时目标随从已经死亡并离场，则不会触发接下来的伤害
		#假设不涉及强制死亡
		for obj in target:
			self.dealsDamage(obj, 3)
			minion, direction = None, ''
			if obj.onBoard and (obj.health < 1 or obj.dead):
				neighbors, dist = self.Game.neighbors2(obj)
				if dist == 1:
					if numpyRandint(2): minion, direction = neighbors[1], 1
					else: minion, direction = neighbors[0], 0
				elif dist < 0: minion, direction = neighbors[0], 0
				elif dist == 2: minion, direction = neighbors[0], 1
			#开始循环
			while minion: #如果下个目标没有随从了，则停止循环
				self.dealsDamage(minion, 3)
				if minion.health < 1 or minion.dead:
					neighbors, dist = self.Game.neighbors2(minion)
					minion = None
					if direction:
						if dist > 0: minion = neighbors[2-dist]
						else: break
					else:
						if dist in (1, -1): minion = neighbors[0]
						else: break
				else: break
		
	
class ShadowCouncil(Spell):
	Class, school, name = "Warlock", "Fel", "Shadow Council"
	numTargets, mana, Effects = 0, 1, ""
	description = "Replace your hand with random Demons. Give them +2/+2"
	name_CN = "暗影议会"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		game, ID = self.Game, self.ID
		if ownHand := game.Hand_Deck.hands[self.ID]:
			pool = self.rngPool("Demons")
			demons = [card(game, ID) for card in numpyChoice(pool, len(ownHand), replace=True)]
			game.Hand_Deck.extractfromHand(None, self.ID, getAll=True, enemyCanSee=False)
			self.addCardtoHand(demons, ID)
			self.giveEnchant(demons, 2, 2, source=ShadowCouncil, add2EventinGUI=False)
		
	
class UnstableFelbolt(Spell):
	Class, school, name = "Warlock", "Fel", "Unstable Felbolt"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 3 damage to an enemy minion and a random friendly one"
	name_CN = "不稳定的邪能箭"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		damage = self.calcDamage(3)
		for obj in target:
			self.dealsDamage(obj, damage)
			if ownMinions := self.Game.minionsonBoard(self.ID):
				self.dealsDamage(numpyChoice(ownMinions), damage)
		
	
class ImprisonedScrapImp(Minion_Dormantfor2turns):
	Class, race, name = "Warlock", "Demon", "Imprisoned Scrap Imp"
	mana, attack, health = 2, 3, 3
	numTargets, Effects, description = 0, "", "Dormant for 2 turns. When this awakens, give all minions in your hand +2/+1"
	name_CN = "被禁锢的拾荒小鬼"
	def awakenEffect(self):
		self.giveEnchant([card for card in self.Game.Hand_Deck.hands[self.ID] if card.category == "Minion"], 2, 1,
						 source=ImprisonedScrapImp, add2EventinGUI=False)
		
	
class KanrethadEbonlocke(Minion):
	Class, race, name = "Warlock", "", "Kanrethad Ebonlocke"
	mana, attack, health = 2, 3, 2
	name_CN = "坎雷萨德·埃伯洛克"
	numTargets, Effects, description = 0, "", "Your Demons cost (1) less. Deathrattle: Shuffle 'Kanrethad Prime' into your deck"
	index = "Legendary"
	aura, deathrattle = ManaAura_KanrethadEbonlocke, Death_KanrethadEbonlocke
	
	
class KanrethadPrime(Minion):
	Class, race, name = "Warlock", "Demon", "Kanrethad Prime"
	mana, attack, health = 8, 7, 6
	name_CN = "终极坎雷萨德"
	numTargets, Effects, description = 0, "", "Battlecry: Summon 3 friendly Demons that died this game"
	index = "Battlecry~Legendary~Uncollectible"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if tups := self.Game.Counters.examDeads(self.ID, veri_sum_ls=2, cond=lambda card: "Demon" in card.race):
			tups = numpyChoice(tups, min(3, len(tups)), replace=False)
			self.summon([self.Game.fabCard(tup, self.ID, self) for tup in tups])
		
	
class Darkglare(Minion):
	Class, race, name = "Warlock", "Demon", "Darkglare"
	mana, attack, health = 3, 3, 4
	numTargets, Effects, description = 0, "", "After your hero takes damage, refresh a Mana Crystals"
	name_CN = "黑眼"
	trigBoard = Trig_Darkglare		
	
	
class NightshadeMatron(Minion):
	Class, race, name = "Warlock", "Demon", "Nightshade Matron"
	mana, attack, health = 4, 5, 5
	name_CN = "夜影主母"
	numTargets, Effects, description = 0, "Rush", "Rush. Battlecry: Discard your highest Cost card"
	index = "Battlecry"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if indices := pickInds_HighestAttr(self.Game.Hand_Deck.hands[self.ID]):
			self.Game.Hand_Deck.discard(self.ID, numpyChoice(indices))
		
	
class TheDarkPortal(Spell):
	Class, school, name = "Warlock", "Fel", "The Dark Portal"
	numTargets, mana, Effects = 0, 4, ""
	description = "Draw a minion. If you have at least 8 cards in hand, it costs (5) less"
	name_CN = "黑暗之门"
	def effCanTrig(self):
		self.effectViable = len(self.Game.Hand_Deck.hands[self.ID]) > 7
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		minion, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Minion")
		if entersHand and len(self.Game.Hand_Deck.hands[self.ID]) > 7: ManaMod(minion, by=-5).applies()
		
	
class HandofGuldan(Spell):
	Class, school, name = "Warlock", "Shadow", "Hand of Gul'dan"
	numTargets, mana, Effects = 0, 6, ""
	description = "When you play or discard this, draw 3 cards"
	name_CN = "古尔丹之手"
	def whenDiscarded(self):
		for _ in (0, 1, 2): self.Game.Hand_Deck.drawCard(self.ID)
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in (0, 1, 2): self.Game.Hand_Deck.drawCard(self.ID)
		
	
class KelidantheBreaker(Minion):
	Class, race, name = "Warlock", "", "Keli'dan the Breaker"
	mana, attack, health = 6, 3, 3
	name_CN = "击碎者克里丹"
	numTargets, Effects, description = 1, "", "Battlecry: Destroy a minion. If drawn this turn, instead destroy all minions except this one"
	index = "Battlecry~Legendary"
	def numTargetsNeeded(self, choice=0):
		return 1 if self.enterHandTurn < self.Game.turnInd else 0
		
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj is not self and obj.onBoard
		
	def effCanTrig(self):
		self.effectViable = self.enterHandTurn >= self.Game.turnInd
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if self.enterHandTurn >= self.Game.turnInd: self.Game.kill(self, self.Game.minionsonBoard(exclude=self))
		elif target: self.Game.kill(self, target)
		
	
class EnhancedDreadlord(Minion):
	Class, race, name = "Warlock", "Demon", "Enhanced Dreadlord"
	mana, attack, health = 8, 5, 7
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Summon a 5/5 Dreadlord with Lifesteal"
	name_CN = "改进型恐惧魔王"
	deathrattle = Death_EnhancedDreadlord
	
	
class DesperateDreadlord(Minion):
	Class, race, name = "Warlock", "Demon", "Desperate Dreadlord"
	mana, attack, health = 5, 5, 5
	name_CN = "绝望的恐惧魔王"
	numTargets, Effects, description = 0, "Lifesteal", "Lifesteal"
	index = "Uncollectible"
	
	
class ImprisonedGanarg(Minion_Dormantfor2turns):
	Class, race, name = "Warrior", "Demon", "Imprisoned Gan'arg"
	mana, attack, health = 1, 2, 2
	numTargets, Effects, description = 0, "", "Dormant for 2 turns. When this awakens, equip a 3/2 Axe"
	name_CN = "被禁锢的 甘尔葛"
	def awakenEffect(self):
		self.equipWeapon(FieryWarAxe(self.Game, self.ID))
		
	
class SwordandBoard(Spell):
	Class, school, name = "Warrior", "", "Sword and Board"
	numTargets, mana, Effects = 1, 1, ""
	description = "Deal 2 damage to a minion. Gain 2 Armor"
	name_CN = "剑盾猛攻"
	def available(self):
		return self.selectableMinionExists()
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		self.dealsDamage(target, self.calcDamage(2))
		self.giveHeroAttackArmor(self.ID, armor=2)
		
	
class CorsairCache(Spell):
	Class, school, name = "Warrior", "", "Corsair Cache"
	numTargets, mana, Effects = 0, 2, ""
	description = "Draw a weapon. Give it +1 Durability"
	name_CN = "海盗藏品"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		weapon, mana, entersHand = self.drawCertainCard(lambda card: card.category == "Weapon")
		if entersHand: self.giveEnchant(weapon, 0, 1, source=CorsairCache)
		
	
class Bladestorm(Spell):
	Class, school, name = "Warrior", "", "Bladestorm"
	numTargets, mana, Effects = 0, 3, ""
	description = "Deal 1 damage to all minions. Repeat until one dies"
	name_CN = "剑刃风暴"
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for _ in range(14):
			if objs := self.Game.minionsonBoard():
				if any(obj.health < 1 or obj.dead for obj in self.dealsDamage(objs, self.calcDamage(1))[0]):
					break
			else: break
		
	
class BonechewerRaider(Minion):
	Class, race, name = "Warrior", "", "Bonechewer Raider"
	mana, attack, health = 3, 3, 3
	name_CN = "噬骨骑兵"
	numTargets, Effects, description = 0, "", "Battlecry: If there is a damaged minion, gain +1/+1 and Rush"
	index = "Battlecry"
	def effCanTrig(self):
		self.effectViable = any(minion.dmgTaken > 0 for minion in self.Game.minionsonBoard())
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		if any(minion.dmgTaken > 0 for minion in self.Game.minionsonBoard()):
			self.giveEnchant(self, 1, 1, effGain="Rush", source=BonechewerRaider)
		
	
class BulwarkofAzzinoth(Weapon):
	Class, name, description = "Warrior", "Bulwark of Azzinoth", "Whenever your hero would take damage, this loses 1 Durability instead"
	mana, attack, durability, Effects = 3, 1, 4, ""
	name_CN = "埃辛诺斯壁垒"
	index = "Legendary"
	trigBoard = Trig_BulwarkofAzzinoth
	
	
class WarmaulChallenger(Minion):
	Class, race, name = "Warrior", "", "Warmaul Challenger"
	mana, attack, health = 3, 1, 10
	name_CN = "战槌挑战者"
	numTargets, Effects, description = 1, "", "Battlecry: Choose an enemy minion. Battle it to the death!"
	index = "Battlecry"
	def targetExists(self, choice=0, ith=0):
		return self.selectableMinionExists(3 - self.ID, choice)
		
	def targetCorrect(self, obj, choice=0, ith=0):
		return obj.category == "Minion" and obj.ID != self.ID and obj.onBoard
		
	def playedEffect(self, target=(), comment="", choice=0, posinHand=-2):
		for obj in target: #该随从会连续攻击那个目标直到一方死亡
			i = 0
			while i < 14 and self.canBattle() and obj.canBattle():
				self.Game.battle(self, obj, resetRedirTrig=False)
				i += 1
		
	
class KargathBladefist(Minion):
	Class, race, name = "Warrior", "", "Kargath Bladefist"
	mana, attack, health = 4, 4, 4
	name_CN = "卡加斯刃拳"
	numTargets, Effects, description = 0, "Rush", "Rush. Deathrattle: Shuffle 'Kargath Prime' into your deck"
	index = "Legendary"
	deathrattle = Death_KargathBladefist
	
	
class KargathPrime(Minion):
	Class, race, name = "Warrior", "", "Kargath Prime"
	mana, attack, health = 8, 10, 10
	name_CN = "终极卡加斯"
	numTargets, Effects, description = 0, "Rush", "Rush. Whenever this attacks and kills a minion, gain 10 Armor"
	index = "Legendary~Uncollectible"
	trigBoard = Trig_KargathPrime
	
	
class ScrapGolem(Minion):
	Class, race, name = "Warrior", "Mech", "Scrap Golem"
	mana, attack, health = 5, 4, 5
	numTargets, Effects, description = 0, "Taunt", "Taunt. Deathrattle: Gain Armor equal to this minion's Attack"
	name_CN = "废铁魔像"
	deathrattle = Death_ScrapGolem
	
	
class BloodboilBrute(Minion):
	Class, race, name = "Warrior", "", "Bloodboil Brute"
	mana, attack, health = 7, 5, 8
	numTargets, Effects, description = 0, "Rush", "Rush. Costs (1) less for each damaged minion"
	name_CN = "沸血蛮兵"
	trigHand = Trig_BloodboilBrute		
	def selfManaChange(self):
		numDamagedMinion = sum(minion.health < minion.health_max for minion in self.Game.minionsonBoard())
		self.mana -= numDamagedMinion
		
	


AllClasses_Outlands = [
	GameRuleAura_KaynSunfury, ManaAura_YsielWindsinger, ManaAura_KanrethadEbonlocke, Death_RustswornInitiate, Death_TeronGorefiend,
	Death_DisguisedWanderer, Death_RustswornCultist, Death_Alar, Death_DragonmawSkyStalker, Death_ScrapyardColossus,
	Death_FelSummoner, Death_CoilfangWarlord, Death_ArchsporeMsshifn, Death_Helboar, Death_AugmentedPorcupine, Death_ZixorApexPredator,
	Death_AstromancerSolarian, Death_Starscryer, Death_MurgurMurgurgle, Death_LibramofWisdom, Death_ReliquaryofSouls,
	Death_Akama, Death_CursedVagrant, Death_LadyVashj, Death_VividSpores, Death_KanrethadEbonlocke, Death_EnhancedDreadlord,
	Death_KargathBladefist, Death_ScrapGolem, Trig_Imprisoned, Trig_InfectiousSporeling, Trig_SoulboundAshtongue,
	Trig_BonechewerBrawler, Trig_MoargArtificer, Trig_BlisteringRot, Trig_Magtheridon, Trig_Replicatotron, Trig_AshesofAlar,
	Trig_BonechewerVanguard, Trig_KaelthasSunstrider, Trig_DemonicBlast, Trig_PriestessofFury, Trig_PitCommander,
	Trig_Ironbark, Trig_Bogbeam, Trig_MarshHydra, Trig_PackTactics, Trig_Evocation, Trig_ApexisSmuggler, Trig_NetherwindPortal,
	Trig_UnderlightAnglingRod, Trig_SethekkVeilweaver, Trig_DragonmawOverseer, Trig_SkeletalDragon, Trig_Ambush, Trig_Bamboozle,
	Trig_DirtyTricks, Trig_ShadowjewelerHanar, Trig_BoggspineKnuckles, Trig_Darkglare, Trig_BulwarkofAzzinoth, Trig_KargathPrime,
	Trig_BloodboilBrute, GameManaAura_KaelthasSunstrider, GameManaAura_AldorAttendant, GameManaAura_AldorTruthseeker,
	Minion_Dormantfor2turns, EtherealAugmerchant, GuardianAugmerchant, InfectiousSporeling, RocketAugmerchant, SoulboundAshtongue,
	BonechewerBrawler, ImprisonedVilefiend, MoargArtificer, RustswornInitiate, Impcaster, BlisteringRot, LivingRot,
	FrozenShadoweaver, OverconfidentOrc, TerrorguardEscapee, Huntress, TeronGorefiend, BurrowingScorpid, DisguisedWanderer,
	RustswornInquisitor, FelfinNavigator, Magtheridon, HellfireWarder, MaievShadowsong, Replicatotron, RustswornCultist,
	RustedDevil, Alar, AshesofAlar, RuststeedRaider, WasteWarden, DragonmawSkyStalker, Dragonrider, KaelthasSunstrider,
	ScavengingShivarra, BonechewerVanguard, SupremeAbyssal, ScrapyardColossus, FelcrackedColossus, FuriousFelfin,
	ImmolationAura, Netherwalker, FelSummoner, KaynSunfury, Metamorphosis, DemonicBlast, ImprisonedAntaen, SkullofGuldan,
	PriestessofFury, CoilfangWarlord, ConchguardWarlord, PitCommander, FungalFortunes, Ironbark, ArchsporeMsshifn,
	MsshifnAttac_Option, MsshifnProtec_Option, MsshifnPrime, FungalGuardian, FungalBruiser, FungalGargantuan, Bogbeam,
	ImprisonedSatyr, Germination, Overgrowth, GlowflySwarm, Glowfly, MarshHydra, YsielWindsinger, Helboar, ImprisonedFelmaw,
	PackTactics, ScavengersIngenuity, AugmentedPorcupine, ZixorApexPredator, ZixorPrime, MokNathalLion, ScrapShot,
	BeastmasterLeoroxx, NagrandSlam, Clefthoof, Evocation, FontofPower, ApexisSmuggler, AstromancerSolarian, SolarianPrime,
	IncantersFlow, Starscryer, ImprisonedObserver, NetherwindPortal, ApexisBlast, DeepFreeze, ImprisonedSungill, SungillStreamrunner,
	AldorAttendant, HandofAdal, MurgurMurgurgle, MurgurglePrime, LibramofWisdom, UnderlightAnglingRod, AldorTruthseeker,
	LibramofJustice, OverdueJustice, LadyLiadrin, LibramofHope, AncientGuardian, ImprisonedHomunculus, ReliquaryofSouls,
	ReliquaryPrime, Renew, DragonmawSentinel, SethekkVeilweaver, Apotheosis, DragonmawOverseer, PsycheSplit, SkeletalDragon,
	SoulMirror, BlackjackStunner, Spymistress, Ambush, BrokenAmbusher, AshtongueSlayer, Bamboozle, DirtyTricks, ShadowjewelerHanar,
	Akama, AkamaPrime, GreyheartSage, CursedVagrant, CursedShadow, BogstrokClacker, LadyVashj, VashjPrime, Marshspawn,
	SerpentshrinePortal, TotemicReflection, Torrent, VividSpores, BoggspineKnuckles, ShatteredRumbler, TheLurkerBelow,
	ShadowCouncil, UnstableFelbolt, ImprisonedScrapImp, KanrethadEbonlocke, KanrethadPrime, Darkglare, NightshadeMatron,
	TheDarkPortal, HandofGuldan, KelidantheBreaker, EnhancedDreadlord, DesperateDreadlord, ImprisonedGanarg, SwordandBoard,
	CorsairCache, Bladestorm, BonechewerRaider, BulwarkofAzzinoth, WarmaulChallenger, KargathBladefist, KargathPrime,
	ScrapGolem, BloodboilBrute, 
]

for class_ in AllClasses_Outlands:
	if issubclass(class_, Card):
		class_.index = "BLACK_TEMPLE" + ("~" if class_.index else '') + class_.index