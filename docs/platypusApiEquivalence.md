? = not sure what this refers to  
name = the equivalent name in our .fbs schema  
\+ = we know what this is but we need to add it  
\- = available through the schema but not directly on the object  

| PlatyApi | Status | Comment |
| --- | --- | --- |
|	(defconst object-data-index -1)               |    	? -  I assume location in memory	-aP	 |
|	(defconst object-data-id 0)                   |    	objectId |
|	(defconst object-data-type 1)                 |    	e.g. 442 (gealleon) | this, class and category need clarification (we have class, type and  typeName)  |
|	(defconst object-data-class 2)                |    	e.g. -292 (galley and its upgrades) |
|	(defconst object-data-category 3)             |    	e.g. 922 (battle ships) |
|	(defconst object-data-cmdid 4)                |    	+ |
|	(defconst object-data-action 5)               |    	+ |
|	(defconst object-data-order 6)                |    	+ |
|	(defconst object-data-target 7)               |    	+ |  add to all objects rather than just units |
|	(defconst object-data-point-x 8)              |    	? |  are the imprecise points just roundings of the floats? yes -aP |
|	(defconst object-data-point-y 9)              |     ? |
|	(defconst object-data-hitpoints 10)           |     hp |
|	(defconst object-data-maxhp 11)               |     maxHp |
|	(defconst object-data-range 12)               |    	+ |
|	(defconst object-data-speed 13)               |    	+ |
|	(defconst object-data-dropsite 14)            |    	+ |
|	(defconst object-data-resource 15)            |    	resourceType |  I think |
|	(defconst object-data-carry 16)               |    	resourceAmount |  I think |
|	(defconst object-data-garrisoned 17)          |    	+ |
|	(defconst object-data-garrison-count 18)      |    	+ |
|	(defconst object-data-status 19)              |     actionState | I think 0:incomplete, 2:active, 3:resource, >=4:inactive |
|	(defconst object-data-player 20)              |     - | objects are nested under a player structure |
|	(defconst object-data-attack-stance 21)       |    	+ |
|	(defconst object-data-action-time 22)         |    	+ |
|	(defconst object-data-target-id 23)           |    	+ |  currently only on unit |
|	(defconst object-data-formation-id 24)        |    	+ |
|	(defconst object-data-patrolling 25)          |    	? |  is this a boolean? need to check |
|	(defconst object-data-strike-armor 26)        |    	+ |
|	(defconst object-data-pierce-armor 27)        |    	+ |
|	(defconst object-data-base-attack 28)         |    	+ |
|	(defconst object-data-locked 29)              |    	? |  is this just locked gates? yes -aP|
|	(defconst object-data-garrison-id 30)         |    	+ |
|	(defconst object-data-train-count 31)         |    	- | buildings have full unit queue |
|	(defconst object-data-tasks-count 32)         |     + |
|	(defconst object-data-attacker-count 33)      |     ? |  the number of objects currently targeting it? damaging it? |
|	(defconst object-data-attacker-id 34)         |     ? |  if more than one object attacking, which one is this? |
|	(defconst object-data-under-attack 35)        |     ? |  is this a boolean? |
|	(defconst object-data-attack-timer 36)        |     + |
|	(defconst object-data-point-z 37)             |     ? |
|	(defconst object-data-precise-x 38)           |     pos.x |
|	(defconst object-data-precise-y 39)           |     pos.y |
|	(defconst object-data-precise-z 40)           |    	pos.z |
|	(defconst object-data-researching 41)         |    	researchingTechId |
|	(defconst object-data-tile-position 42)       |     ? | is this inferable from the precise position |
|	(defconst object-data-tile-inverse 43)        |     ? |  what is the inverse? |
|	(defconst object-data-distance 44)            |     ? |  are these distance just straight line calculations? |
|	(defconst object-data-precise-distance 45)    |     ? |
|	(defconst object-data-full-distance 46)       |     ? |
|	(defconst object-data-map-zone-id 47)         |     zone id on map as defined in RMS |
|	(defconst object-data-on-mainland 48)         |     on player starting zone |
|	(defconst object-data-idling 49)              |     ? |  is this calculated from actionState? |
|	(defconst object-data-move-x 50)              |     ? | are these from the current action? I believe so -aP|
|	(defconst object-data-move-y 51)              |     ? |
|	(defconst object-data-precise-move-x 52)      |     ? |
|	(defconst object-data-precise-move-y 53)      |     ? |
|	(defconst object-data-reload-time 54)         |     + |
|	(defconst object-data-next-attack 55)         |     + |  assuming this means the time? in ms, yes -aP |
|	(defconst object-data-train-site 56)          |     ? |  I think these might be Building.training? |
|	(defconst object-data-train-time 57)          |     ? |  time to train left in seconds (need to verify) -aP
|	(defconst object-data-blast-radius 58)        |     + |
|	(defconst object-data-blast-level 59)         |     + |
|	(defconst object-data-progress-type 60)       |     ? |
|	(defconst object-data-progress-value 61)      |     ? |
|	(defconst object-data-min-range 62)           |     + |
|	(defconst object-data-target-time 63)         |     ? | is the time the unit has spent targeting something? |
|	(defconst object-data-heresy 64)              |     - | available through PlayerInfo.techs |
|	(defconst object-data-faith 65)               |    	- |
|	(defconst object-data-redemption 66)          |    	- |
|	(defconst object-data-atonement 67)           |    	- |
|	(defconst object-data-theocracy 68)           |    	- |
|	(defconst object-data-spies 69)               |    	- |
|	(defconst object-data-ballistics 70)          |    	- |
|	(defconst object-data-gather-type 71)         |     ? |  isn't this the same as @15? used for villagers, can also be done by checking name, see next -aP |
|	(defconst object-data-language-id 72)         |     id in from language file (e.g. Lumberjack -> Houthakker (Dutch) |
