/*
	Copyright (C) 2014 Ryosuke Fukatani All Rights Reserved
	
    This file is part of pylink.

    pylink is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    pylink is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pylink.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <Python.h>
#include <stdio.h>

//#define debug

PyObject *pName, *pModule, *pDict, *pClass, *pInstance;

int main(void){
	double a;
	int i;
	
	printf("start\n");
	
	py_start(0.005,16);
	
	for (i=0;i<1000;i++){
		py_exe(5,&a);
	}
	
	//printf("Return of call @main: %f\n",a);
	
	//py_func("sim_end");
	py_end();
	
	
	return 0;
}

int py_start(double time_step, int divide_num){
    const char *script_name = "sim_test";
    const char *class_name = "time_driven_simulator";
	char *set_func = "set_condition";
	
	
    Py_Initialize();
    pName = PyString_FromString(script_name);
    pModule = PyImport_Import(pName);
	pDict = PyModule_GetDict(pModule);
   
    // Build the name of a callable class 
    pClass = PyDict_GetItemString(pDict, class_name);
    
    
    // Create an instance of the class
    if (PyCallable_Check(pClass))
    {
		pInstance = PyObject_CallObject(pClass, NULL); 
    }
    
    //set inner clas parameter
	PyObject_CallMethod(pInstance, set_func, "(fi)", time_step, divide_num);

	return 0;
}

int py_exe(int a, int *o)
{
	
	PyObject *pValue;
	char *function_name = "get_next_state";
	
	#ifdef debug
    printf("py_exe\n");
    #endif
   	
   	pValue = PyObject_CallMethod(pInstance, function_name,"(i)", a);
    
	if (pValue != NULL) 
    {
		#ifdef debug
		printf("Return of call : %f\n", PyFloat_AsDouble(pValue));
		#endif
		*o=PyFloat_AsDouble(pValue);
		//*o=12;
		Py_DECREF(pValue);
    }
    else 
    {
		PyErr_Print();
    }
    

    return 0;
}

int py_func(char* func_name){
	//#ifdef debug
	printf("func:%s",func_name);
	//#endif
	
	PyObject_CallMethod(pInstance, func_name, NULL);
	return 0;
}


int py_end(void){
	py_func("sim_end");
	
	// Clean up
	Py_DECREF(pModule);
    Py_DECREF(pName);
    Py_Finalize();
    
    return 0;
}