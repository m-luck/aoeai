## Usage

Inject the built dll into the WK process with something like the `testDll.bat` script.
You may need to put `bin\libeay32.dll` in your game / system folder.

The websocket will open at `localhost:8080` - see `browserTest.html` for a simple example usage in JS, and `cpSchemaDef.fbs` for the Flatbuffers schema.

## Building

Clone, init the submodules and then use the visual studio project.
Requires boost, openssl to be installed in the correct places (see the VS project properties for paths)

There are two versions of the reader: the default is compile time restricted to only work on recs, and will be available at `dist/aoc-state-reader.dll`. The second is compiled with `AOCSR_ALLOWLIVE` and will be available at `dist/aoc-state-reader-ALLOWLIVE.dll`. The second version *SHOULD NOT BE RELEASED PUBLICLY* at the present time as it can potentially be used to cheat and currently has no protection.


## Immediate todo
 - refactor to separate the server, flatbuffers, and hooking/asm code
  - app
	- server
	- messages
	- hooks
	


## Feature improvements
 - somehow skip redundant sync actions for rec speedup
 - figure out how to handle projectile ids for teuton bombard towers filled with janissaries correctly

Building
  target / gather point 

Playergit
 currently selected objects ids
 pov
 fog of war


### Notes / random pointers

- add to CE: 
There are selected units
player[0x1c0]  First main unit
player[0x1c4] - player[0x1c4+4*40] All selected units(edited)
PoV: world[0x94]