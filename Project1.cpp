#include <stdio.h>
#include <stdlib.h>
#include <math.h>

//clejjevve

int disq(int a, int b, int c)
{
	int d = b*b - 4 * a*c;
	return d;
}




int main()
{
	int a, b, c;
	scanf_s("%d",&a);
	scanf_s("%d",&b );
	scanf_s("%d",&c);

	int f = disq(a, b, c);
	if (f >= 0)
	{
		double x1 = (-b + sqrt(f)) / (2 * a);
		double x2 = (-b - sqrt(f)) / (2 * a);
		printf("%f \n", x1);
		printf("%f \n", x2);
	}
	else
	{
		printf("Solution isnt exist");
	}

	system("pause");
	return 0;
}