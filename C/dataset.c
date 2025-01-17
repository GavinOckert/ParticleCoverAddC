#include "header.h"

//c doesn't support overloading
void initDataSetBase(DataSet* ds) {
    ds->total_points = 0;
    memset(ds->n_points, 0, sizeof(ds->n_points)); //initialize n_points with 0
}

void initDataSetExtra(DataSet* ds, Environment* envI) {
    ds->total_points = 0;
    //lhs is pointer, consistent with rhs
    ds->env = envI;
    memset(ds->n_points, 0, sizeof(ds->n_points)); 

    for (int i = 0; i < MAX_LAYERS; i++) {
        for (int j = 0; j < MAX_POINTS_FOR_DATASET; j++) { //MAX_POINTS_FOR_DATASET is the max length of vector<Point> vect;
            ds->array[i][j] = (Point){0, 0.0f, 0.0f, 0.0f}; //initialize with default values
        }
    }

}

void importData(DataSet* ds, Point* data_array, int data_array_size) {
    //need data_array_size. we can't eliminate the parameter and count the total number of points because we are adding points, we don't know how many
    ds->total_points = data_array_size;

    for (int i = 0; i < data_array_size; i++) {
        int layer = data_array[i].layer_num - 1;
        if (ds->n_points[layer] < MAX_POINTS_FOR_DATASET) {
            ds->array[layer][ds->n_points[layer]++] = data_array[i];
        }
    }
    //iterating over the layers in DataSet
    for (int i = 0; i < ds->env->num_layers; i++) {
        //sorts the points in the ith layer
        qsort(ds->array[i], ds->n_points[i], sizeof(Point), floatCompare);
    }
}

void addBoundaryPoint(DataSet* ds, float offset) {
    ds->boundaryPoint_offset = offset;

    for (int i = 0; i < ds->env->num_layers; i++) { //num_layers is trapezoid_edges.size(), see environment.c
        if (ds->n_points[i] + 2 <= MAX_POINTS_FOR_DATASET) { //there needs to be room to add the additional points
            //shifting the array to make room for the new point at the beginning. That first point is left uninitialized
            //parameters: (address of where to start writing data, address of what to put where you start writing, number of bytes that need to be moved) 
            memmove(&ds->array[i][1], &ds->array[i][0], ds->n_points[i] * sizeof(Point));

            //inserting at the beginning
            ds->array[i][0].layer_num = i + 1;
            ds->array[i][0].radius = (i + 1) * 5;
            ds->array[i][0].phi = ds->array[i][1].phi;  //1 gets what was originally the index 0, but is not index 1 due to the insertion.
            ds->array[i][0].z = -1 * ds->env->trapezoid_edges[i] - offset;

            //appending at the end
            int lastIndex = ds->n_points[i] + 1;  //after shifting, there's one more point
            ds->array[i][lastIndex].layer_num = i + 1;
            ds->array[i][lastIndex].radius = (i + 1) * 5;
            ds->array[i][lastIndex].phi = ds->array[i][1].phi; //1 gets what was originally the index 0, but is not index 1 due to the insertion.
            ds->array[i][lastIndex].z = ds->env->trapezoid_edges[i] + offset;

            ds->n_points[i] += 2;
        }
    }

    int total = 0;
    //iterating over the layers in DataSet
    for (int i = 0; i < ds->env->num_layers; i++) {
        //like before, sorting the points in the ith layer
        qsort(ds->array[i], ds->n_points[i], sizeof(Point), floatCompare);
        //our code ensures n_points stays up to date and fresh and doesn't need to be recomputed here
        total += ds->n_points[i]; //summing sizes of 1D array
    }
    ds->total_points = total; //size of 2D array, giving total number of points in the dataset

    for (int i = 0; i < ds->env->num_layers; i++) {
        ds->env->trapezoid_edges[i] += offset;
    }   

}