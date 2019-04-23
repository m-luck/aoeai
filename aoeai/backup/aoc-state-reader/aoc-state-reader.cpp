// aoc-state-reader.cpp : Defines the entry point for the DLL application.
#include "stdafx.h"
#include "aoc-socket.h"

HANDLE g_hTimer;

void CALLBACK startTickerThread(PVOID lpParam, BOOLEAN reserved);

bool keepRunningTicker = true;
BOOL APIENTRY DllMain(HMODULE hModule, DWORD  ul_reason_for_call, LPVOID lpReserved) {
	switch (ul_reason_for_call) {
	case DLL_PROCESS_ATTACH:
		AllocConsole();
		AttachConsole(GetCurrentProcessId());
		freopen("CON", "w", stdout);
		printf("DLL attached and running!\n");
		// we are just setting this up so that it gets called asynchronously outside of the dllmain environment
		CreateTimerQueueTimer(&g_hTimer, NULL, startTickerThread, NULL, 100, 0, 0);
		
		break;
	case DLL_THREAD_ATTACH:

		
		break;
	case DLL_THREAD_DETACH:
		
		break;
	case DLL_PROCESS_DETACH:
		keepRunningTicker = false;
		break;
	}
	return TRUE;
}

VOID CALLBACK startTickerThread(PVOID lpParam, BOOLEAN reserved) {
	std::thread(startSocketServer, &keepRunningTicker).join();
}





