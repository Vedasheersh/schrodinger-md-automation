text = '''1	ACALD
2	ACALD
	
3	ALDD2x
	
4	CS
	
5	FBA
6	FBA
	
7	FUM
8	FUM
	
9	GAPD
	
10	GLCP
	
11	GLGC
12	GLGC
13	GLGC
	
14	GLNS
15	GLNS
16	GLNS
17	GLNS
	
18	ICDHyr
	
19	LDH_L
20	LDH_L
	
21	MDH
	
22	ME1
	
23	MTHFD
	
24	PFK
25	PFK
	
26	PGK
	
27	PGMT
	
28	PPDK
	
29	PTAr
	
30	TKT1
31	TKT1
32	TKT1
33	TKT1'''

import os

for each in text.split('\n'):
	if each.strip():
		num, name = each.split()
		tag = num+'_'+name.strip()
		os.mkdir(tag)
