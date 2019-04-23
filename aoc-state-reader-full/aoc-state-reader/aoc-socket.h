#pragma once

#include "stdafx.h"
#include "cpSchemaDef_generated.h"
using namespace AOC;
using namespace std;
using WsServer = SimpleWeb::SocketServer<SimpleWeb::WS>;


typedef unsigned int *pointer;
typedef unsigned int rawPointer;

// used to set speedup values... the name is a hint
void setSpeedupValues();

/*
The main entry point - this sets up a server and starts a polling loop
*/
void startSocketServer(bool *keepTicking);

/*
This checks the game time, and if it is >tickInterval since the last game time it will compose and send a message
*/
void handleGameTick();

/*
entry point for building a message - takes the current game time
*/
shared_ptr<WsServer::OutMessage> buildMessage(unsigned int gt);

/*
build the player info part of a message
*/
flatbuffers::Offset<PlayerInfo> buildPlayerInfo(int playerId, pointer &resourcesP, flatbuffers::FlatBufferBuilder &builder);

flatbuffers::Offset<flatbuffers::Vector<flatbuffers::Offset<Tech>>> buildTechs(pointer &techTreeP, flatbuffers::FlatBufferBuilder &builder);

flatbuffers::Offset<Tech> * buildTech(short int expectedTechId, unsigned int techMasterP, unsigned int techLiveP, flatbuffers::FlatBufferBuilder &builder);

flatbuffers::Offset<PlayerObjects> buildPlayerObjectList(int playerId, pointer &pObjectListP, flatbuffers::FlatBufferBuilder &builder);

void handleMapObjectTick(std::vector<flatbuffers::Offset<MapObject>> &mVector, flatbuffers::FlatBufferBuilder &builder);

flatbuffers::Offset<CommonObjectInfo> buildCommonObjectInfo(pointer &objectP, flatbuffers::FlatBufferBuilder &builder);

flatbuffers::Offset<Unit> buildUnit(pointer &objectP, flatbuffers::FlatBufferBuilder &builder);
flatbuffers::Offset<Building> buildBuilding(pointer &objectP, flatbuffers::FlatBufferBuilder &builder);
flatbuffers::Offset<MapObject> buildMapObject(pointer &objectP, flatbuffers::FlatBufferBuilder &builder);