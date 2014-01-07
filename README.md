Hunt the Wumpus
---------------

An implementation in Python 2.7 of the original "Hunt the Wumpus" game by
Gregory Yob circa the mid 1970s, as described in
[The Best of Creative Computing Volume 1](http://www.atariarchives.org/bcc1/showpage.php?page=247). This
implementation remains true to the original game play, including bugs
(features?) that are present in the original implementation.  I've made only
typographical adjustments and the addition of a 'q' key to quit.

	$ python main.py

A sample run through
====================

	Instructions (y-n)? y

	Welcome to 'Hunt the Wumpus'.

	The wumpus lives in a cave of 20 rooms. Each room has 3 tunnels
	leading to other rooms. (Look at a dodecahedron to see how this works
	- if you don't know what a dodecahedron is, ask someone).

	Hazards:
	   Bottomless Pits - two rooms have bottomless pits in them. If you go
		  there, you fall into the pit (and lose!)

	   Super Bats - two other rooms have super bats. If you go there, a
		  bat grabs you and takes you to some other room at random (which
		  might be troublesome).

	Wumpus:
	   The wumpus is not bothered by the hazards (he has sucker feet and
	   is too big for a bat to lift).  Usually he is asleep. Two things
	   wake him up: your entering his room or your shooting an arrow.

	   If the wumpus wakes, he moves (p=.75) one room or stays still
	   (p=.25). After that, if he is where you are, he eats you up (and you
	   lose!)

	You:
	   Each turn you may move or shoot a crooked arrow.

	   Moving: you can go one room (through one tunnel).

	   Arrows: you have 5 arrows. you lose when you run out.  Each arrow
		  can go from 1 to 5 rooms.  You aim by telling the computer the
		  room #s you want the arrow to go to.  If the arrow can't go that
		  way (ie no tunnel) it moves at random to the next room.  If the
		  arrow hits the wumpus, you win.  If the arrow hits you, you
		  lose.

	Warnings:
	   When you are one room away from the wumpus or a hazard, the computer
	   says:

	   Wumpus - 'I smell a wumpus'
	   Bat    - 'Bats nearby'
	   Pit    - 'I feel a draft'

	Hunt the Wumpus

	You are in room 17
	Tunnels lead to 7, 16, 18
	Shoot, Move or Quit (s-m-q)? m
	Where to? 7

	I feel a draught.
	You are in room 7
	Tunnels lead to 6, 8, 17
	Shoot, Move or Quit (s-m-q)? m
	Where to? 17

	You are in room 17
	Tunnels lead to 7, 16, 18
	Shoot, Move or Quit (s-m-q)? m
	Where to? 16

	[...]

	You are in room 3
	Tunnels lead to 2, 4, 12
	Shoot, Move or Quit (s-m-q)? m
	Where to? 2

	Bats nearby!
	You are in room 2
	Tunnels lead to 1, 3, 10
	Shoot, Move or Quit (s-m-q)? m
	Where to? 1
	Zap -- super bat snatch! Elsewhereville for you!

	Bats nearby!
	You are in room 5
	Tunnels lead to 1, 4, 6
	Shoot, Move or Quit (s-m-q)? m
	Where to? 6

	Bats nearby!
	You are in room 6
	Tunnels lead to 5, 7, 15
	Shoot, Move or Quit (s-m-q)? m
	Where to? 15

	You are in room 15
	Tunnels lead to 6, 14, 16
	Shoot, Move or Quit (s-m-q)? m
	Where to? 6

	Bats nearby!
	You are in room 6
	Tunnels lead to 5, 7, 15
	Shoot, Move or Quit (s-m-q)? m
	Where to? 7

	I feel a draught.
	You are in room 7
	Tunnels lead to 6, 8, 17
	Shoot, Move or Quit (s-m-q)? m
	Where to? 17

	You are in room 17
	Tunnels lead to 7, 16, 18
	Shoot, Move or Quit (s-m-q)? m
	Where to? 18

	I smell a wumpus!
	I feel a draught.
	You are in room 18
	Tunnels lead to 9, 17, 19
	Shoot, Move or Quit (s-m-q)? s
	No. of rooms (1-5)? 1
	Room? 9
	Aha! You got the wumpus!

	Hee hee hee - the Wumpus'll getcha next time!!
	Same set-up (y-n)? y
