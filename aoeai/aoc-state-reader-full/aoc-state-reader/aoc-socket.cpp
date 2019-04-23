#include "stdafx.h"
#include "aoc-socket.h"
#include "aoc-structs.h"
#include <stdint.h>
#include <iostream>
using namespace std;
using namespace AOC;
using WsServer = SimpleWeb::SocketServer<SimpleWeb::WS>;

#ifdef AOCSR_ALLOWLIVE
bool allowUseLive = true;
#else
bool allowUseLive = false;
#endif // AOCSR_ALLOWLIVE


//global flags for various debugging
bool debugInConsole = true;
bool debugTechsInConsole = false;
bool debugObjectsInConsole = false;
bool debugProjectilesInConsole = false;
bool debugDamagesInConsole = false;



//global config (can be modified by any incoming websocket message of the right format)
bool hasReceivedConfig = false;

unsigned int configTickInterval = 5000;
unsigned int configMapObjectTickInterval = 1000 * 15;
int configUpdateCycles = 1;

Restriction configPlayerRestriction = Restriction_All;
std::vector<uint8_t> configPlayerRestrictV = {};

Restriction configObjectRestriction = Restriction_All;
std::vector<uint32_t> configObjectRestrictV = {};



//offsets and static pointers
unsigned int baseAddress = 0;
unsigned int worldPOffset = 0x2B7668;
unsigned int inGameOffset = 0x283CC0;
unsigned int recDetectOffset = 0x3A52E4;// 3 =  rec, 4 = sp
unsigned int selectedUnitOffset = 0x1c0;



//initial value set low so that any first tick will trigger a loop (let's say you inject the dll 4 hours into a game)
int lastProcessedTick = -864000000;
int lastProcessedMapObjectTick = -864000000;
unsigned int gameTickNow = 0;//this is the current game tick, can be set in multiple places
unsigned int currentTick = 0; // this is the tick as seen by handleGameTick (used for timing of outgoing messages)

// these are for tracking projectiles throughout a game
unsigned int nextProjectileId = 1;
unordered_map<int, int> ourProjectileIdToOwnerMap; // this builds during the game
unordered_map<int, int> currentGameProjectileToOurIdMap;//this gets thrashed as game projectile ids are recycled
std::vector<ProjectileFire> projectileFireV;
std::vector<Damage> damageV;


// when continuing to run this tracks how many games have been started
unsigned int instanceGameNo = 0;
bool isFinished = false;
bool finishMessageSent = false;
std::chrono::time_point<std::chrono::steady_clock> gameStartedRealTime;
bool finishElapsePrinted = false;

//dynamically assigned pointers, vals etc 
pointer worldP;
volatile bool * inGame;
volatile unsigned int * volatile gameTick;
volatile uint8_t * volatile recDetect;
volatile bool isRec = false;
volatile uint8_t * volatile finishDetect; //a pointer to either the place for sp, or for rec
uint8_t finishDetectIsFinish; // what we expect if the game has indeed finished
volatile int * volatile gameSpeedupAllow; //loation to change to allow speed up of game (also disables pause)
volatile unsigned char * volatile jumpSlowpokeRecCode; // location of the slowpoke asm to change
// volatile uint8_t * volatile selectedUnit;
unsigned char disableSlowpokeAsm = (unsigned char)0xEB;
unsigned char originalSlowpokeAsm = (unsigned char)0x74;


// if name == 'main':
//     import time
//     proc_name = "AoK HD.exe"
//     pm.load_process(proc_name)
//     game = Game()
//     if game is not None:
//         t = game.update()
//     ##print(game.pov.resources.values[0]) # food
//     #print(game.pov.resources.values[1]) # Wood

//     p = game.pov  # p = player 
//     score = 0
//     # Military - Military score is 20% of the resource value (cost) of all enemy units and buildings each player destroyed or converted.
//     score += p.resources.values[170]0.2 # units value razed
//     score += p.resources.values[172]0.2 # buildings value razed

//     # Economy score is 10% of all resources each player currently has or has paid in tribute,
//     # Reousrces
//     score += p.resources.values[0]*0.1 + p.resources.values[1] * 0.1 + p.resources.values[2] *0.1 + p.resources.values[3] *0.1
//     # plus 20% of the resource value of surviving units and standing buildings (except Castles or Wonders).
//     score += p.resources.values[164] * 0.2 
//     score += p.resources.values[165] * 0.2
//     # Units TODO

//     # Technology score is 20% of the resource value of every technology each player has researched, plus 10 points for every 1% of the map explored.
//     score += p.resources.values[99] * 0.2
//     # 10 for 1% of the map   Note that this is approximation! It can have numbers after decimal point 91.5%
//     score += p.resources.values[22] * 10

//     #Society score is 20% of the cost of the Castles and Wonders each player has constructed.
//     # NONE already calculated in Enconomy??
//     score += p.resources.values[184] * 0.2
//     print(score)


//this just sets up commonly used pointers so we only have to do this once
void normalisePointers() {
	// this is just for convenience
	if (debugInConsole) {
		configTickInterval = 2000;
	    configPlayerRestriction = Restriction_InList;
		configPlayerRestrictV = {1};
		//configObjectRestriction = Restriction_InList;
		//configObjectRestrictV = { 60 };
		//configUpdateCycles = 2;
	}
	if (baseAddress < 1) {
		baseAddress = (unsigned int) GetModuleHandle(NULL);
	}
	worldP = (pointer)(baseAddress + worldPOffset);
	inGame = (bool *)baseAddress + inGameOffset;
	recDetect = (uint8_t *) baseAddress + recDetectOffset;
	gameSpeedupAllow = (int *)(baseAddress + 0x391208);
	jumpSlowpokeRecCode = (unsigned char *)(baseAddress + 0xc916);
  // selectedUnit = (pointer)(baseAddress + selectedUnitOffset);
	setSpeedupValues();
}


// utility function for setting an arbitrary protected value of known size
void setProtectedValue(void * ptr, void * value, int size) {
	DWORD old;
	if (VirtualProtect(ptr, size, PAGE_EXECUTE_READWRITE, &old) == 0) {
		printf("Couldn't unprotect?! @ %p [%zu]\n", ptr, 1);
	}
	else {
		memcpy(ptr, value, size);
		DWORD old1;
		VirtualProtect(ptr, size, old, &old1);
	}
}


void setSpeedupValues() {
	if (configUpdateCycles != 1) {
		*gameSpeedupAllow = -1;
		setProtectedValue((void *) jumpSlowpokeRecCode, &disableSlowpokeAsm, 1);
	}
	else {
		*gameSpeedupAllow = 0;
		setProtectedValue((void *)jumpSlowpokeRecCode, &originalSlowpokeAsm, 1);
	}
}


//called when we detect a new game has started / is starting - resets all the global variables that track game state
void initialiseNewGameTracking() {
	if (debugInConsole) {
		printf("New game detected, resetting global state \n");
	}
	gameStartedRealTime = std::chrono::high_resolution_clock::now();
	finishElapsePrinted = false;
	gameTick = (unsigned int *)(*worldP + 0x10);
	lastProcessedTick = -864000000;
	lastProcessedMapObjectTick = -864000000;
	instanceGameNo++;
	nextProjectileId = 1;
	ourProjectileIdToOwnerMap.clear();
	currentGameProjectileToOurIdMap.clear();
	projectileFireV.clear();
	damageV.clear();
	finishMessageSent = false;
	isRec = *recDetect == 3;
	if (isRec) {
		pointer temp = pointer(*worldP + 0xC);
		pointer temp1 = pointer(*temp + 0x01614);
		finishDetect = (uint8_t *)(*temp1 + 0x4);
		finishDetectIsFinish = 0;	
	}
	else {
		finishDetect = (uint8_t *)(*worldP + 0x29);
		finishDetectIsFinish = 1;
	}
}



// the type for the update function
typedef void(__stdcall *updateFunc)();
// initialise as pointing to nothing
updateFunc originalUpdateFunc = 0;

/*
a1 - total attack bonuses of attacking unit
 0: mangonel secondary
 2: hero attacking tower, also wolf, chu ko nu secondary, just a bit odd
 3: mango main attack, ram main and splash
 4: elephant thinking about attack mango, knight attacking blacksmith, villager - normal melee?
 5: skirm, archer, mangudai, scorpion, castle secondary
 6: tower , chu ko nu, castle main, arambai
infoAboutAttackingObject (pointer to a structure also pointed to by master object) - if secondary (projectile) then not present?
percentOfDamageDone - for eg area of effect damage for eg mangonel
a4
objectMakingTheAttack - pointer to the object making the attack

target seems to be saved in ecx

returns primary damage done, seems to apply secondary damage directly
*/
typedef void(__stdcall *damageDoneFunc)();
damageDoneFunc  originalCalculateDamage = 0;

volatile int cycles = 1;

//volatile int updateReturn = 0;

#pragma runtime_checks ("", off) // this removes the asm around function calls
/*
original update func starts at 0042D300
pointer is at 00636484
*/
__declspec(naked) void replacementUpdateFunc() {
	if (!gameTick) {
		gameTick = (unsigned int *)(*worldP + 0x10);
	}
	__asm {
		mov cycles,0x1
	};
	// don't loop for the first update 
	while (!isFinished && currentTick > 0 && (cycles < configUpdateCycles || configUpdateCycles < 0) && (isRec || allowUseLive)) {
		__asm {
			push ecx
		};
		originalUpdateFunc();
		handleGameTick();
		cycles++;
		__asm {
			pop ecx
		};
	}
	originalUpdateFunc();
	__asm {
		push eax
	};
	handleGameTick();

	__asm {
		pop eax
		ret
	}
}
#pragma runtime_checks ("", restore)

int localAttackerId = 0;
int localProjectileId = 0;
int localDamagedId = 0;
unsigned int localTopOfStack = 0;
unsigned int localObjectMakingTheAttack = 0;
unsigned int localTargetPointer = 0;
float damageDone = 0;
void __stdcall handleDamageDone();

#pragma runtime_checks ("", off) // this removes the asm around function calls


__declspec(naked) void replacementCalculateDamage() {
	
	__asm {
		push ecx
		mov ecx, [esp + 0x4]
		mov localTopOfStack, ecx
		pop ecx
		mov localTargetPointer, ecx
		mov localObjectMakingTheAttack, edi // the fifth argument, seems to be in edi
		pop edx // remove the stack return point so the stack is in the same place for the original call
	}
	originalCalculateDamage();
	//this is the offset for the function return point - if it returns here then it seems to be actually doing damage, if it returns to 005CFC1A then it is part of targeting ai
	if (localTopOfStack == 0x005CE616) {
		__asm {
			fst damageDone // get the result
		}
		handleDamageDone();
	}
	__asm {
		push localTopOfStack
		ret
	}
}
#pragma runtime_checks ("", restore)
/*
This is currently broken for additional bombard tower shots - they are multiple primaries rather than true secondaries, so we don't get the projectile id right. Not 100% sure how to solve this at the moment.
 When calculateDamage is called for primary attacks, the projectile (if any_ seems to be in esp+0xC4. So we could potentially switch to matching all projectiles with their id directly, but we would need a way to detect whether a particular damage was with a projectile. If we could do that then we can simply say 
   if (isProjectile) {
      if (localObjectMakingTheAttack.id > 0) { // secondaries will already be the projectile (with negative ids)
      localObjectMakingTheAttack = esp+0xC4 // the projectile for a primary attack
	  }
   }
   and remove the code below that assigns primary projectiles to their parent unit rather than to their projectile id

   At present this only seems to affect teuton bombard towers stuffed with janis
 -

*/
void __stdcall handleDamageDone() {
	damageDone = damageDone < 1 ? 1 : damageDone;
	localAttackerId = *(int *)(localObjectMakingTheAttack + 0x4);
	localProjectileId = 0;
	if (currentGameProjectileToOurIdMap.count(localAttackerId)) {
		localProjectileId = currentGameProjectileToOurIdMap.at(localAttackerId);
		localAttackerId = ourProjectileIdToOwnerMap.at(localProjectileId);
	}
	localDamagedId = *(int *)(localTargetPointer + 0x4);;
	damageV.push_back(Damage(*gameTick, localAttackerId, localProjectileId, localDamagedId, damageDone));

	if (debugDamagesInConsole) {
		printf("     *** Damage done - gt: %u, attackerId: %i, projectileId: %u, damagedId: %i, damageDone: %f \n",
			*gameTick,
			localAttackerId,
			localProjectileId,
			localDamagedId,
			damageDone
		);
	}
}

int currentProjectileGameId = 0;
int currentProjectilePointer = 0;
short currentProjectileObjectType = 0;
int currentAttackerId = 0;
int currentTargetId = 0;
bool currentIsPrimary = false;

void __stdcall handleProjectileCreation() {

	ourProjectileIdToOwnerMap.insert_or_assign(nextProjectileId, currentAttackerId);
	//primary projectiles show up as their originating unit ids in calculateDamage - doing this allows us to track these projectiles as projectiles
	if (currentIsPrimary) {
		currentGameProjectileToOurIdMap.insert_or_assign(currentAttackerId, nextProjectileId);
	}
	// in cases where the unit dies before the projectile damages the damage function also gets the projectile id rather than the attacker, so we assign projectile in both places
	currentGameProjectileToOurIdMap.insert_or_assign(currentProjectileGameId, nextProjectileId);
	
	projectileFireV.push_back(ProjectileFire(*gameTick, nextProjectileId, currentAttackerId, currentTargetId, currentProjectileObjectType, currentIsPrimary));

	if (debugProjectilesInConsole) {
		printf("      >>> Projectile fired - gt: %u, projP: %X, gameprojid: %i, projid: %u, attacker: %i, target: %i, type: %hi, isPrimary: %hhi \n",
			*gameTick,
			currentProjectilePointer,
			currentProjectileGameId,
			nextProjectileId,
			currentAttackerId,
			currentTargetId,
			currentProjectileObjectType,
			currentIsPrimary
		);
	}

	nextProjectileId++;
	
}

int localReturnPoint = 0;
int secondaryStackValue = 0;
__declspec(naked) void projectileCreationRetReplacement() {
	// function starts at 0058B670
	__asm {
		mov currentProjectilePointer, eax
		push eax
		push ecx		
		mov ecx, [eax + 0x4]
		mov currentProjectileGameId, ecx
		mov ecx, [eax + 0x8] //mo pointer
		mov eax, [ecx + 0x10]//mo type
		mov currentProjectileObjectType, ax
		mov eax, [esp + 0x14]
		mov localReturnPoint, eax
		push ebx
	}	
		// this is the return point for secondary mangonel, chukonu etc
	if (localReturnPoint == 0x004C30D1) {
		currentIsPrimary = false;
		__asm {
			mov ebx, [esp + 0x30]  // if there is a target it is in stack at esp+0x24 at beginning of function (+ 3 pushes = 0x30). for mangonels esp + 0x30 is the number from the while loop
			mov secondaryStackValue, ebx
			mov eax, esi			//attacker is in esi 
		}
		if (secondaryStackValue < 1000) { // this is not a pointer so this must be a mangonel attack ground
			__asm {
				mov ebx, eax
			}
		}
	}
	else if (localReturnPoint == 0x005ce0b0) {// this is the return point for primary chukonu and primary attack generally
		currentIsPrimary = true;
		__asm {
			mov ebx, edi // target is in edi
			mov eax, esi //attacker is in esi, 
		}
	}
	else if (localReturnPoint == 0x005CE244) {//return point for priimary mangonel when attacking ground
		currentIsPrimary = true;
		__asm {
			mov ebx, edi // there is no target, but we make them equal for the code below
			mov eax, edi //attacker in edi
		}
	}
	else if (localReturnPoint == 0x004C311B) {//bombard tower secondary cannonballs - pretty similar to the return point for secondaries generally but they are primary attacks - this breaks our current logic
		currentIsPrimary = true;
		__asm {
			mov ebx, [esp + 0x30] // target, bombard towers will always have one
			mov eax, esi //attacker in esi
		}
	}
	else {
		
		printf("Unknown return point when looking for projectile owner: %X", localReturnPoint);
	}

	__asm {
		mov eax, [eax + 0x4]
		mov currentAttackerId, eax
		mov ebx, [ebx + 0x4]
		mov currentTargetId, ebx
		pop ebx
		push edx
	}
	// this is an attack ground
	if (currentAttackerId == currentTargetId) {
		currentTargetId = 0;
	}

	handleProjectileCreation();
	__asm {		
		pop edx
		pop ecx
		pop eax
		add esp, 0Ch // these are the two asm statements we are overwriting
		retn 10h
	}
}





uint8_t projectileCreationRetAssembly[6] = {0xE9, 0x00, 0x00,  0x00,  0x00,  0x90};

int offsetForProjectileHook1 = 0x18b6d5;
int offsetForProjectileHook2 = 0x18b720;
int offsetForProjectileHook3 = 0x18b736;

void installProjectileHook(int offset) {

	int projectileCreationRetReplacementI = (((int)&projectileCreationRetReplacement) - (baseAddress + offset + 5));
	auto projectileHookP = (void *)(baseAddress + offset);
	auto assemblyPointer = (pointer *)(((int)&projectileCreationRetAssembly) + 1);
	memcpy(assemblyPointer, &projectileCreationRetReplacementI, 4);
	setProtectedValue(projectileHookP, (void *)&projectileCreationRetAssembly, 6);
}

// absolute = 58b6d5 or 4C318D
/*
  - sub_58B670 is what we want to overwrite?
  - called by sub_4C2F90
  - called by sub_4c2AE0 -- this is a while loop  
  */

// we need not a function pointer, but a pointer to a function pointer...

void installHooks() {


	void * replacementUpdateFuncP = (void *)&replacementUpdateFunc;
	void * replacementCalculateDamageP = (void *)&replacementCalculateDamage;

	
	auto updateFuncP = (pointer *) (baseAddress + 0x236484);
	originalUpdateFunc = (updateFunc)*updateFuncP;
	setProtectedValue(updateFuncP, (void *)&replacementUpdateFuncP, 4);

	auto damageFuncBuildingP = (pointer *)((baseAddress + 0x23bfe4));
	auto damageFuncUnitP = (pointer *)((baseAddress + 0x23BB7C));

	originalCalculateDamage = (damageDoneFunc)*damageFuncBuildingP;
	setProtectedValue(damageFuncBuildingP, (void *)&replacementCalculateDamageP, 4);
	setProtectedValue(damageFuncUnitP, (void *)&replacementCalculateDamageP, 4);

	installProjectileHook(offsetForProjectileHook1);
	installProjectileHook(offsetForProjectileHook2);
	installProjectileHook(offsetForProjectileHook3);

	printf("Update, damage and projectile hooks installed\n");
	
}


// set up the server
WsServer server;

auto &listenEP = server.endpoint["^/listen/?$"];

void startSocketServer(bool *keepTicking) {
	server.config.port = 8080;

	listenEP.on_message = [](shared_ptr<WsServer::Connection> /*connection*/, shared_ptr<WsServer::InMessage> in_message) {

		try {
			auto size = (*in_message).size();
			char *buffer = new char[size];
			(*in_message).read(buffer, size);
			auto configMessage = GetConfigMessage(buffer);
			configTickInterval = configMessage->tickInterval();
			configMapObjectTickInterval = configMessage->mapObjectTickInterval();

			configPlayerRestriction = configMessage->playerRestriction();
			configPlayerRestrictV = {};
			auto pRestrictV = configMessage->playerRestrictV();
			if (pRestrictV) {
				for (unsigned int i = 0; i < pRestrictV->size(); i++) {
					configPlayerRestrictV.push_back(pRestrictV->Get(i));
				}
			}

			configObjectRestriction = configMessage->objectRestriction();
			configObjectRestrictV = {};
			auto oRestrictV = configMessage->objectRestrictV();
			if (oRestrictV) {
				for (unsigned int i = 0; i < oRestrictV->size(); i++) {
					configObjectRestrictV.push_back(oRestrictV->Get(i));
				}
			}
			configUpdateCycles = configMessage->updateCycles();
			setSpeedupValues();

			hasReceivedConfig = true;
		}
		catch (const std::exception& e) { // reference to the base of a polymorphic object
			std::cout << e.what(); // information from length_error printed
		}
		catch (...) {
			// could we use verify from flatbuffers above to anticipate errors of this kind?
			printf("Uncatchable error when parsing incoming socket message");
		}
	};

	normalisePointers();
	thread server_thread([]() {
		server.start();
	});
	printf("WS server started\n");
	installHooks();

	while (*keepTicking) {
		std::this_thread::sleep_for(std::chrono::seconds(60 * 60));
		// if we let this thread terminate we get a fatal exception - this should be solvable in other ways but for now we will just sleep it for an hour every hour...
	}
}



bool waitForTickIncrease = true;
unsigned int lastSeenTick = 0;

void handleGameTick() {
	gameTickNow = *gameTick;
	if (gameTickNow > 0) {
		if (currentTick < 1 || gameTickNow < currentTick) {
			waitForTickIncrease = true;
			currentTick = gameTickNow;
		}
	}
	// the idea is that we need to wait for a tick increase after it seems like a new game has started - otherwise some of the memory we want to read doesn't seem to have been set yet
	if (waitForTickIncrease) {
		if (gameTickNow > currentTick) {
			initialiseNewGameTracking();
			waitForTickIncrease = false;
		} else {
			return;
		}
	}

	currentTick = gameTickNow;

	isFinished = (currentTick > 0 && *finishDetect == finishDetectIsFinish);
	if (isFinished && !finishElapsePrinted) {
		finishElapsePrinted = true;
		auto elapsed = std::chrono::high_resolution_clock::now() - gameStartedRealTime;
		auto elapsedMS = std::chrono::duration_cast<std::chrono::milliseconds>(elapsed).count();
		printf("Game finished - real time elapsed:  %lld\n", elapsedMS);
	}
	if (hasReceivedConfig || debugInConsole) {	
	
		//printf("gameno: %u, ingame: %hhu, isRec: %hhu, finishDetect: %hhu, finishDetectIsFinish: %hhu \n", instanceGameNo, *inGame, isRec, *finishDetect, finishDetectIsFinish);
		
		if ((currentTick - lastProcessedTick > configTickInterval) || (isFinished && !finishMessageSent)) {
			if (isFinished) {
				finishMessageSent = true;
				if (debugInConsole) {
					printf("Game end detected, sending finish message\n");
				}

			}
			lastProcessedTick = currentTick;
			if (!isRec && !allowUseLive) {
				return;
			}
			if (debugInConsole) {
				//printf("Handle game tick isRec: %i, allowUseLive: %i\n", isRec, allowUseLive);
				printf("Building message for game tick: %u\n", currentTick);
			}
			auto conns = listenEP.get_connections();
			if (!(conns.empty()) || debugInConsole) {
				auto msg = buildMessage(currentTick);
				for (auto &a_connection : conns) {
					//130 is for sending binary data
					a_connection->send(msg, NULL, 130);
				}
				//clear the global vectors
				projectileFireV.clear();
				damageV.clear();
			}
		}

	}

}



bool includePlayer(short playerId) {
	switch (configPlayerRestriction) {
	case Restriction_All: return true;
	case Restriction_InList: return (find(configPlayerRestrictV.begin(), configPlayerRestrictV.end(), playerId) != configPlayerRestrictV.end());
	}
	return false;
}

bool includeObjectClass(uint8_t oClass) {
	switch (configObjectRestriction) {
	case Restriction_All: return true;
	case Restriction_InList: return (find(configObjectRestrictV.begin(), configObjectRestrictV.end(), oClass) != configObjectRestrictV.end());
	}
	return false;

}


shared_ptr<WsServer::OutMessage> buildMessage(unsigned int gt) {
	flatbuffers::FlatBufferBuilder builder(100 * 1000);

	pointer playerListP = pointer (*worldP + 0x4C);
	short numberOfPlayers = * (short *) (*worldP + 0x48);
	std::vector<flatbuffers::Offset<PlayerInfo>> piVector;
	std::vector<flatbuffers::Offset<PlayerObjects>> poVector;
	if (*playerListP > 0) {
		for (short playerId = 0; playerId < numberOfPlayers; playerId++) {
			if (includePlayer(playerId)) {
				pointer pAreaP = pointer(*playerListP + (playerId * 4));
				if (*pAreaP > 0) {
					if (playerId > 0) {
						// for now we won't include gaia in the player info, because there doesn't seem to be much of interest there
						piVector.push_back(buildPlayerInfo(playerId, pAreaP, builder));
					}
					poVector.push_back(buildPlayerObjectList(playerId, pAreaP, builder));

				}


			}
		}
	}
	auto players = builder.CreateVector(piVector);
	auto playerOs = builder.CreateVector(poVector);
	float *mcWood = (float *)(*worldP + 0x228);
	float *mcFood = (float *)(*worldP + 0x22C);
	float *mcStone = (float *)(*worldP + 0x230);
	auto mapName = (char *)(*((pointer) (baseAddress + 0x3912A0)) + 0x1447);

	auto mc = MarketCoefficients(*mcWood, *mcFood, *mcStone);

	auto mapnameB = builder.CreateString(mapName);

	auto projectilesFired = builder.CreateVectorOfStructs(projectileFireV);
	auto damages = builder.CreateVectorOfStructs(damageV);

	GameMessageBuilder gmBuilder(builder);
	gmBuilder.add_tick(gt);
	gmBuilder.add_instanceGameNumber(instanceGameNo);
	gmBuilder.add_finished(isFinished);
	gmBuilder.add_marketCoefficients(&mc);
	gmBuilder.add_mapName(mapnameB);
	gmBuilder.add_players(players);
	gmBuilder.add_objects(playerOs);
	gmBuilder.add_projectilesFired(projectilesFired);
	gmBuilder.add_damages(damages);

	auto gmMessage = gmBuilder.Finish();
	auto outMessage = make_shared<WsServer::OutMessage>();
	builder.Finish(gmMessage);
	const char* pos = (const char*) builder.GetBufferPointer();
	(*outMessage).write(pos, builder.GetSize());

	return outMessage;
}

flatbuffers::Offset<PlayerInfo> buildPlayerInfo(int playerId, pointer &pAreaP, flatbuffers::FlatBufferBuilder &builder) {


	pointer techTreeP = pointer(*pAreaP + 0x12A0);
	
	auto techs = buildTechs(techTreeP, builder);

	pointer resourcesP = pointer(*pAreaP + 0xa8);
	char *name = (char *) *pointer(*pAreaP + 0x98);

	/*A2 - 1 = winner?, 2 = resigned, 2= defeated
      A3 - 1 = resigned, 0 = still playing or whatever
	*/
	uint8_t *pState = (uint8_t *)pointer(*pAreaP + 0xA2);
	bool *resigned = (bool *) pointer(*pAreaP + 0xA3);
	PlayerState playerState = PlayerState_Playing;
	switch (*pState) {
		case 0:
		break;
		case 1: 
			playerState = PlayerState_Winner;
		break;
		case 2: 
			if (*resigned) {
				playerState = PlayerState_Resigned;
			}
			else {
				playerState = PlayerState_Defeated;	
			}
		break;
	}

	int32_t *mainUnitSelectedP = pointer(*pAreaP + 0x1c4);
	
	auto pName = builder.CreateString(name);

	PlayerInfoBuilder pBuilder(builder);
	reslist &ls = *((reslist *)*resourcesP);
	pBuilder.add_playerId(playerId);
	pBuilder.add_playerName(pName);
	pBuilder.add_playerState(playerState);
	pBuilder.add_food(ls.food);
	pBuilder.add_wood(ls.wood);
	pBuilder.add_stone(ls.stone);
	pBuilder.add_gold(ls.gold);
	pBuilder.add_headroom(ls.populationFreeRoom);
	pBuilder.add_population(ls.population);
	pBuilder.add_populationCap(ls.populationCap);
	pBuilder.add_civilianPopulation(ls.civilianPopulation);
	pBuilder.add_militaryPopulation(ls.militaryPopulation);
	pBuilder.add_percentMapExplored(ls.percentMapExplored);
	pBuilder.add_techs(techs);
	pBuilder.add_mainSelected(mainUnitSelectedP)
	return pBuilder.Finish();
}


flatbuffers::Offset<flatbuffers::Vector<flatbuffers::Offset<Tech>>> buildTechs(pointer &techTreeP, flatbuffers::FlatBufferBuilder &builder) {

	pointer techTreeLiveP = pointer(*techTreeP);

	pointer techTreeDefP = pointer(*techTreeP + 0x8);
	pointer techTreeMasterP = pointer(*techTreeDefP);
	int numberOfTechs = (int)*pointer(*techTreeDefP + 0x4);

	std::vector<flatbuffers::Offset<Tech>> tVector;
	for (int i = 0; i < numberOfTechs; i++) {
			unsigned int techMasterP = unsigned int(*techTreeMasterP + (i * 0x44));
			unsigned int techLiveP = unsigned int(*techTreeLiveP + (i * 0x10));
			auto mT = buildTech(i, techMasterP, techLiveP, builder);
			if (mT != nullptr) {
				tVector.push_back(*mT);
			}
	}

	return builder.CreateVector(tVector);
}
// we need to change this to return a maybe, but that doesn't seem easily doable in c++


flatbuffers::Offset<Tech> outTech;
flatbuffers::Offset<Tech> * buildTech(short int techIndex, unsigned int techMasterP, unsigned int techLiveP, flatbuffers::FlatBufferBuilder &builder) {
	short *techState = (short *)pointer(techLiveP + 0x4);


	char *techName = (char *)*pointer(techMasterP + 0x0);
	float *techTime = (float *)pointer(techLiveP);
	short *techId = (short *)pointer(techMasterP + 0x28);
	//ignore techs that can't be researched or that don't actually exist
	if (*techState < TechState_CanResearchLater || *techId < 1) {
		return nullptr;
	}
	if (debugTechsInConsole) {
		printf("Tech name: %s (%hi), techIndex: %hi, tech state: %hi, tech time: %f \n",
			techName,
			*techId,
			techIndex,
			*techState,
			*techTime
		);
	}
	TechBuilder oBuilder(builder);
	oBuilder.add_techIdIndex(techIndex);
	oBuilder.add_techIdGame(*techId);
	oBuilder.add_techState(static_cast<TechState>(*techState));
	oBuilder.add_timePassed(*techTime);
	outTech = oBuilder.Finish();
	return &outTech;
	
}

void handleObjectList(pointer &objectListP, std::vector<flatbuffers::Offset<Unit>> &uVector, std::vector<flatbuffers::Offset<Building>> &bVector, std::vector<flatbuffers::Offset<MapObject>> &mVector, flatbuffers::FlatBufferBuilder &builder) {

	pointer objectListActualPs = pointer(*objectListP + 0x4);
	int numberOfObjects = (int)*pointer(*objectListP + 0x8);

	for (int i = 0; i < numberOfObjects; i++) {
		pointer objectP = pointer(*objectListActualPs + (i * 4));
		uint8_t *objectClass = (uint8_t *)pointer(*objectP + 0x4e);
		if (includeObjectClass(*objectClass)) {
			switch (*objectClass) {
			case 70:
				uVector.push_back(buildUnit(objectP, builder));
				break;
			case 80:
				bVector.push_back(buildBuilding(objectP, builder));
				break;
			default:
				mVector.push_back(buildMapObject(objectP, builder));
				break;
			}
		}
	}


}

flatbuffers::Offset<PlayerObjects> buildPlayerObjectList(int playerId, pointer &pAreaP, flatbuffers::FlatBufferBuilder &builder) {
	
	std::vector<flatbuffers::Offset<Unit>> uVector;
	std::vector<flatbuffers::Offset<Building>> bVector;
	std::vector<flatbuffers::Offset<MapObject>> mVector;


	pointer liveObjectListP = pointer(*pAreaP + 0x78);
	handleObjectList(liveObjectListP, uVector, bVector, mVector, builder);

	pointer sleepingObjectListP = pointer(*pAreaP + 0x7C);

	if (playerId == 0) {
		//this will be for gaia's sleeping objects, which we don't want all the time
		if (includeObjectClass(10)) {
			if (currentTick - lastProcessedMapObjectTick > configMapObjectTickInterval) {
				lastProcessedMapObjectTick = currentTick;
				handleObjectList(sleepingObjectListP, uVector, bVector, mVector, builder);
			}
		}		
	}
	else {
		handleObjectList(sleepingObjectListP, uVector, bVector, mVector, builder);
	}

	auto units = builder.CreateVector(uVector);
	auto buildings = builder.CreateVector(bVector);
	auto mos = builder.CreateVector(mVector);

	PlayerObjectsBuilder pBuilder(builder);
	pBuilder.add_playerId(playerId);
	pBuilder.add_units(units);
	pBuilder.add_buildings(buildings);
	pBuilder.add_mapObjects(mos);
	return pBuilder.Finish();

}

flatbuffers::Offset<Unit> buildUnit(pointer &objectP, flatbuffers::FlatBufferBuilder &builder) {

	auto common = buildCommonObjectInfo(objectP, builder);

	pointer actionListP = pointer(*objectP + 0x108);
	pointer actionListFirstLevelP = pointer(*actionListP + 0x08);
	UnitBuilder oBuilder(builder);

	if (actionListFirstLevelP) {
		pointer actionFirstEntryP = pointer(*actionListFirstLevelP);
		if (actionFirstEntryP) {
			ActionState *actionState = (ActionState *)pointer(*actionFirstEntryP + 0xC);

			int *actionTargetId = (int *) pointer(*actionFirstEntryP + 0x18);
			float *pos = (float *) pointer(*actionFirstEntryP + 0x20);
			auto position = Pos((pos[0]), (pos)[1], (pos)[2]);

			if (debugObjectsInConsole) {
				printf("Action state: %hhu, actionTarget: %i,  pos: (%f,%f,%f) \n",
					*actionState,
					*actionTargetId,
					pos[0],
					pos[1],
					pos[2]
				);
			}

			oBuilder.add_actionState(*actionState);
			oBuilder.add_actionTargetPos(&position);

		}
		else {
			oBuilder.add_actionState(ActionState_None);
		}
	}
	else {
		oBuilder.add_actionState(ActionState_None);
	}



	oBuilder.add_common(common);
	return oBuilder.Finish();
}

flatbuffers::Offset<Building> buildBuilding(pointer &objectP, flatbuffers::FlatBufferBuilder &builder) {

	auto common = buildCommonObjectInfo(objectP, builder);

	std::vector<UnitQueue> qVector;
	
	pointer queueP = pointer(*objectP + 0x1C0);
	short int numberLeftToParse = *(short int *)(*objectP + 0x1C8);
	
	if (*queueP > 0) {
		uint8_t i = 0;
		while (numberLeftToParse > 0 && i < 16) {
			short *uqVals = ((short *)(*queueP + (i * 4)));
			if (debugObjectsInConsole) {
				printf("Queue: unitid %hi, number %hi \n",
					uqVals[0],
					uqVals[1]
				);
			}
			qVector.push_back(UnitQueue(uqVals[0], uqVals[1]));
			i++;
			numberLeftToParse = numberLeftToParse - uqVals[1];
		}
	}

	short trainingType = 0;
	float trainingTimer = 0;
	pointer trainingP = pointer(*objectP + 0x1CC);

	if (*trainingP) {
		pointer trainingP1 = pointer(*trainingP + 0x8);
		if (*trainingP1) {
			pointer trainingP2 = pointer(*trainingP1);
			if (*trainingP2) {
				trainingType = *(short *)pointer(*trainingP2 + 0x40);
				trainingTimer = *(float *)pointer(*trainingP2 + 0x44);
			
			}

		}
	}
	auto queue = builder.CreateVectorOfStructs(qVector);
	BuildingBuilder oBuilder(builder);
	oBuilder.add_common(common);
	oBuilder.add_queue(queue);
	if (trainingType) {
		if (debugObjectsInConsole) {
			printf("Training: unitid %hi, timer %f \n",
				trainingType,
				trainingTimer
			);
		}
		auto ut = UnitTraining(trainingType, trainingTimer);
		oBuilder.add_training(&ut);
	}

	pointer researchingP = pointer(*objectP + 0x1A0);
	if (*researchingP) {
		pointer researchingP1 = pointer(*researchingP + 0x8);
		if (*researchingP1) {
			pointer researchingP2 = pointer(*researchingP1);
			if (*researchingP2) {
				short *researchingTechId = (short *)pointer(*researchingP2 + 0x40);
				oBuilder.add_researchingTechId(*researchingTechId);
				if (debugObjectsInConsole) {
					printf("Researching: %hu\n",
						*researchingTechId
					);
				}
			}
		}
	}

	
	return oBuilder.Finish();
}

flatbuffers::Offset<MapObject> buildMapObject(pointer &objectP, flatbuffers::FlatBufferBuilder &builder) {
	

	auto common = buildCommonObjectInfo(objectP, builder);
	MapObjectBuilder oBuilder(builder);
	oBuilder.add_common(common);
	return oBuilder.Finish();
}

flatbuffers::Offset<CommonObjectInfo> buildCommonObjectInfo(pointer &objectP, flatbuffers::FlatBufferBuilder &builder) {

	int *objectId = (int *) pointer(*objectP + 0x4);	
	ObjectState *objectState = (ObjectState *)pointer(*objectP + 0x48);
	uint8_t *objectClass = (uint8_t *) pointer(*objectP + 0x4e);
	float *hp = (float *)pointer(*objectP + 0x30);
	float *pos = (float *)pointer(*objectP + 0x38);
	auto position = Pos((pos[0]), (pos)[1], (pos)[2]);

	short *resourceType = (short *)pointer(*objectP + 0x4C);
	float *resourceAmount = (float *)pointer(*objectP + 0x44);



	// aimodule is at 6c 
	pointer aiModuleP = pointer(*objectP + 0x6c);
	

	pointer masterObjectP = pointer(*objectP + 0x8);
	short *objectType = (short *)pointer(*masterObjectP + 0x10);
	char *objectTypeName = (char *) *pointer(*masterObjectP + 0x08);
	short *maxHp = (short *)pointer(*masterObjectP + 0x2A);
	

	if (debugObjectsInConsole) {


		printf("Object id: %d (%hu) >"
			"    pointer: %X"
			"    type: %hu (%s)\n",
			*objectId,
			*objectClass,
			*objectP,
			*objectType,
			objectTypeName
		);


     // full object debugging
	/*	printf("Object id: %d (%hu) > \n"
			"    - pointer: %p\n"
			"    - type: %hu (%s)\n"
			"    - state: %hhu\n"
			"    - hp: %f / %hu\n"
			"    - pos: (%f,%f,%f)\n"
			"    - restype: %hi\n"
			"    - resAmount: %f\n"
			"    - currentTargetId: %d\n"
			"    - totalDamageDoneToCurrentTarget: %f\n"
			"    - totalDamageDone: %f\n",
			*objectId,
			*objectClass,
			*objectP,
			*objectType,
			objectTypeName,
			*objectState,
			*hp,
			*maxHp,
			pos[0],
			pos[1],
			pos[2],
			*resourceType,
			*resourceAmount,
			currentTargetIdDebug,
			totalDamageDoneToCurrentTargetDebug,
			totalDamageDoneDebug
		);*/
	}

	auto oTypeName = builder.CreateString(objectTypeName);
	CommonObjectInfoBuilder oBuilder(builder);
	oBuilder.add_objectId(*objectId);
	oBuilder.add_objectClass(*objectClass);
	oBuilder.add_objectType(*objectType);
	oBuilder.add_objectTypeName(oTypeName);
	oBuilder.add_objectState(*objectState);
	oBuilder.add_pos(&position);
	oBuilder.add_hp(*hp);
	oBuilder.add_maxHp(*maxHp);
	oBuilder.add_resourceType(*resourceType);
	oBuilder.add_resourceAmount(*resourceAmount);
	return oBuilder.Finish();

}
