from HS_AcrossPacks import TrigsDeaths_AcrossPacks
from HS_Core import TrigsDeaths_Core
from HS_Outlands import TrigsDeaths_Outlands
from HS_Academy import TrigsDeaths_Academy
from HS_Darkmoon import TrigsDeaths_Darkmoon
from HS_Barrens import TrigsDeaths_Barrens
from HS_Stormwind import TrigsDeaths_Stormwind


Dict_TrigsDeaths = {}
for dic in (TrigsDeaths_AcrossPacks, TrigsDeaths_Core,
			TrigsDeaths_Outlands, TrigsDeaths_Academy, TrigsDeaths_Darkmoon,
			TrigsDeaths_Barrens, TrigsDeaths_Stormwind):
	Dict_TrigsDeaths.update(dic)