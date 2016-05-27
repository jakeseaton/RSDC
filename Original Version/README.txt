Tyler Lau
2016.06.21

This is the original implementation of a modification of Van Everbroeck and Polinsky (2003)'s simulation. This neural net takes in

~*~

INPUT LAYER
A stem can have a maximum of 36 phonemes (6 syllables, 6 potential phonemes)

Potential phonemes are: p, t, k, b, d, g, f, v, s, z, h, m, n, w, r, l, y, i, u, e, o, a, * (= schwa), - (no phoneme)

-

Each phoneme is represented by 11 features, from Chomsky & Halle (1968):
1) Syllabic (Vowels VS Non-Vowels)
2) Consonantal (Consonants VS Glides & Vowels)
3) Voice (Voiced VS Unvoiced)
4) Continuant (Continuants VS Stops/Nasals)
5) Strident (f, v, s, z, VS others)
6) Nasal (m, n VS others)
7) Anterior (front—includes l and r unlike English VS back)
8) ??? (a, o VS others)
9) Grave (u, o, a, schwa, labial, velar VS coronal)
10) Round (w, u, o VS others)
11) ??? (u, a, ptkfsh VS others)

36 * 11 = 396 nodes

-

8 nodes are used to represent humanness

1 1 1 1 0 0 0 0 —> male human
0 0 0 0 1 1 1 1 —> female human
0 0 0 0 0 0 0 0 —> non-human

-

Original had Slavic gender, but they are irrelevant (12 nodes)

1 1 1 1 0 0 0 0 0 0 0 0 —> masculine
0 0 0 0 1 1 1 1 0 0 0 0 —> feminine
0 0 0 0 0 0 0 0 1 1 1 1 —> neuter

-

Case Frequencies Implemented as how many times case goes into model—estimated by Polinsky and van Everbroeck

		Human				Non-Human
	Sg		Pl		Sg			Pl
Nom	8		3		4			2
Acc	4.5		2.5		7			2
Gen	4		2		2			1

In this instantiation, we get rid of human frequencies, because the token frequency is ALREADY accounted for—humans are already much more common than non-humans.

***

HIDDEN LAYER

30 hidden nodes

***

OUTPUT LAYER

Mapped to four outputs (P&VE only did gender)

Gender (3):
	M: 1 0 0
	F: 0 1 0
	N: 0 0 1

Declension (5):
	I: 1 0 0 0 0
	II: 0 1 0 0 0
	III: 0 0 1 0 0 
	IV: 0 0 0 1 0
	V: 0 0 0 0 1

Number (2):
	SG: 1 0
	PL: 0 1

Case (3):
	If Case Hierarchy implemented (consider Acc closer to Nom and Gen than Nom and Gen to each other)
		Nom: 1 0 0
		Acc: 1 1 0
		Gen: 1 1 1

	If Case Hierarchy not Implemented (all three equidistant)
		Nom: 1 0 0
		Acc: 0 1 0
		Gen: 0 0 1

*******************
RELEVANT PARAMETERS
*******************

Genitive Drop (Gnv)
	If T, genitive is dropped
	If F, genitive is not dropped
Case Hierarchy
Features 1: Changed features to 1 instead of 0.9