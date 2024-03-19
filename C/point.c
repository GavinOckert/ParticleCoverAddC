#include "header.h"

int Point_load(Point* p)
{
	//reads input of the form (layer_num,radius,phi,z) to populate point structure. 1 if worked, 0 if not.
	if (scanf("(%d,%f,%f,%f)", &p->layer_num, &p->radius, &p->phi, &p->z) == 4)
	{
		return 1;
	}

	return 0;
}

//CREATE_VECTOR_OF_T(Point) //macro invocation. creates alias of PointVector and generates Point specific vector functions. 
