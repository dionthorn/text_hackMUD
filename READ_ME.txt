Goals:
	- Handle 20 Clients at a time. Unsure of Current Ability
	- MUD style text based rpg with a 'hacking' theme

Game Design:
	- Players First Steps
		- Upon starting the Client it will try to verify with server if there is a history of login from Client.
		- Registering only requires a unique username and any password
		- Once Client has registered or logged on then they can issue commands to the Server.
		- Client once logged on or registered should type '/help' without quotes.		

	- Player Info
		- Unique IP Address, is how other players will find you in the game. ex: 255:255:255 = 255^3 possible player accounts. May be changed for Credits.
		- Credits, how you buy things or pay off debts
		- Computer, you start with one
			- CPU
			- GPU
			- RAM
			- HDD
			- SSD
			- NET
		- Bandwidth
	- Servers
		- Public FTP
			- Anyone Can Access Safely
		- Any IP is also a server so any player can be accessed
			- Not Safe ensure you cover your tracks
			- Each players server keeps logs
			- Logs can be Deleted or Protected
	- File System
		- Each Program takes computer resources
		- Hacking Programs
			- FireScan  : Check a given IP for activity
			- AdminPull : Check a verified active IP for weak admin protection and attempt to gain access
			- LogDel    : Del, Alter logs
		- Defense Programs
			- FireWall  : Defend against Port Scan
			- AdminPass : Defend against AdminPull
			- LogRec    : Recover logs
		- Once Admin is gained on target system you can move files to and from it or execute files as well as attempt to delete or alter logs
		