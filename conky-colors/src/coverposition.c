#include "coverposition.h"
#include "variables.h"

//Cover Position
void coverposition () {
	if (cpu == 1)
		yc += 134;
	else {
		yc += 116;
		for (i = 1; i <= cpu; i++)
		yc += 12;
	}
	if (aptget == True)
		yc += 13;
	if (gmail == True)
		yc += 13;
	if (set_battery == True)
		yc += 14;
	if (swap == True)
		yc += 26;
	if (set_process == True) {
		yc += 14;
		for (i = True; i <= proc; i++)
		yc += 12;
	}
	if (nodata == False) {
		if (clocktype == 1)
			yc += 58;
			else
				if (clocktype == 2)
					yc += 60;
			else
				if (clocktype == 3)
					yc += 28;
			else
				yc += 62;
		if (set_calendar > 0)
			yc += 76;
	}
	if (set_photo == 1 || set_photo == 2) {
		yc += 126;
	}
	if (cover == 3 || cover == 6 || cover == 7)
		yc -= 2;
}

void coverposition_cairo () {
	if (cpu == 1 || cputype == True)
		yc += 278;
	else {
		yc += 214;
		for (i = 1; i <= cpu; i++)
			yc += 64;
	}
	if (swap == True)
		yc += 64;
	if (clocktype == 4)
		yc += 64;
	else if(clocktype == 5)
		yc += 104;
}

void coverposition_ring () {
	if (cpu > 2)
		yc += 64;
	yc += 447;
}
