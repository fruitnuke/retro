## Hunt the Wumpus

An implementation in Python 2.7 of the original "Hunt the Wumpus" game by
Gregory Yob circa the mid 1970s, as described in
[The Best of Creative Computing Volume 1](http://www.atariarchives.org/bcc1/showpage.php?page=247). This
implementation remains true to the original game play, including bugs
(features?) that are present in the original implementation.  I've made only
typographical adjustments and the addition of a 'q' key to quit.

	$ python wumpus/wumpus.py

## Hammurabi

[Hammurabi](https://en.wikipedia.org/wiki/Hamurabi) is a game of city
management, the text-based ancestor of games like Civilization. You play the
role of ruler of Sumeria over a decade, during which your decision as to how
much to feed your people, how much land to buy and sell and harvest, decide the
fate of your city. Written in Python 3 and based on the 1978 implementation in
[BASIC Computer Games](http://atariarchives.org/basicgames/showpage.php?page=78).

    $ python3 hammurabi/hammurabi.py

## Dukedom

A more complex simulation of city management than Hammurabi,
[Dukedom](http://en.wikipedia.org/wiki/Dukedom_%28game%29)
places you as the Duke of a duchy, competing with other duchies to build your
population and land, defeat them in battle, and ultimately challenge the King
for the crown. Dukedom adds war, taxes, population moral, disease and a random
generation system based on normal curves that means every game will be
different.

Based on the implementation in
[Big Computer Games 1984](http://www.atariarchives.org/bigcomputergames/showpage.php?page=11)
(see the same for playing instructions). Created by Vince Talbot in 1976,
revised by Jamie Hanrahan and converted to Microsoft Basic by Richard Kaapke.

	$ python3 dukedom/dukedom.py
