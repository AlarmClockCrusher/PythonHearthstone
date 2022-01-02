from Panda.UICommonPart import *


class Run_1PGame(Panda_UICommon):
	def prepareDeckBuilderPanel(self):
		self.deckBuilder = DeckBuilderHandler(self, for1P=True)

	def startGame(self, btn):
		HD = self.deckBuilder
		if  (deck1 := HD.decks[1]) and (deck2 := HD.decks[2]):
			seed = datetime.now().microsecond
			self.boardID = numpyChoice(BoardIndex)

			if self.np_CardZoomIn: self.np_CardZoomIn.removeNode()
			self.Game = Game(self)
			self.Game.initialize_Details(self.boardID, int(seed), RNGPools, HD.heroes[1], HD.heroes[2], deck1=deck1,
										 deck2=deck2)
			self.clearDrawnCards()
			self.deckBuilder.root.stash()
			self.initMulliganDisplay(for1P=True)
		else: Btn_NotificationPanel(GUI=self, text="玩家套牌为空，不能开始游戏", acknowledge=True)

	def initMulligan(self, btn):
		self.stage = 0
		self.addaButton("Button_Concede", "Back", self.render, pos=(20.5, -8, 1.1), text="Back", textColor=white,
						removeAfter=True, func=self.back2Layer1)

		print("Start mulligan", self.Game)
		indices1 = [i for i, status in enumerate(self.mulliganStatus[1]) if status]
		indices2 = [i for i, status in enumerate(self.mulliganStatus[2]) if status]
		for i in indices1: self.Game.mulligans[1][i].btn.np.removeNode()
		for i in indices2: self.Game.mulligans[2][i].btn.np.removeNode()
		# 直到目前为止不用创建需要等待的sequence
		self.Game.Hand_Deck.mulliganBoth(indices1, indices2)


if __name__ == "__main__":
	Run_1PGame().run()