
# ParticlePartition

## Environment and Data Objects
Before we do anything, we must import the data.py module and create an environment. An environment object contains information about the kind of collider that the data will be generated in. It can be initialized with a constructor, and it has the following attributes 
```
env = Environment() 
print(env.top_layer_lim)        # a float representing the upper and lower limits of the top layer (default 1.0m)
print(env.bottom_layer_lim)     # a float representing the upper and lower limits of layer 0 in m (default 0.15m) 
print(env.layers)               # a integer representing the number of layers, excluding layer 0 (default 5) 
print(env.radii)                # a float representing the distance between consecutive layers in m (default 5.0m)
```

Once we have generated the environment, we can generate a dataset by constructing the `Dataset` object with the environment and number of points per layer as its argument. 
``` 
data = DataSet(env, n_points = 150) 
```
To access the data, we just need to call `data.array`, which gives us a $L \times N$ matrix $A$, where ($L$ is the number of layers and $N$ is the number of points in each layer). Furthermore, for each $i = 1, \ldots, L$, row $i$ is already sorted in its points from least to greatest. Plotting it usig the `plot` method should give a shape that approximately looks like an inverted symmetric trapezoid. 

## Point and Line Objects 
A line can be characterized by two things: a point $(x_0, y_0)$ on the line and its slope $m$. It is clear that $y_0$, the height, should be $0$, but the $x_0$ may vary (by default we set $x_0 = 0$). Therefore, a line should have two parameters: the $x_0$ value of its originating point and the slope $m$. We can construct it by calling: 
``` 
line = Line(env, start, slope)
``` 
where `env` is the embedding environment, `start` is $x_0$, and `slope` is $m$. It would be nice to add a check within this constructor to determine whether the inputted slope is viable (i.e. within the range of the maximum and minimum slope), but I thought this might take away computational speed, so I did not implement this. 

Ultimately, the line object is described by the `env.layer` = $5$ points of the line that lies on each layer. This should also be stored in the `points` attribute. 

A `LineGenerator` object simply generates lines within an environment and that has a start value equal to what is inputted. 
```
lg = LineGenerator(env, start) 
``` 

We can either choose to generate `n` lines with equal spacing across the entire environment (like a grid over angles) by calling `generateGridLines(n)` or generate them according to a uniform distribution (over the angle space $\theta = \arctan(m)$) by calling `generateRandomLines(n)`. They both return a Python list of `Line` objects. 


## Constructing Covers

We define three things:
 - A **cover** $C$ is a finite family of patches $C = \{P_i\}_{i=1}^n$. 
 - A **patch** $P$ is a list of $L$ superpoints, with the 1st superpoint element representing the superpoint of the 1st layer. 
 - A **superpoint** $S$ is a collection of 16 consecutive points in one layer. 
For further developers, I would recommend only adding extra attributes and methods to the `Patch` class. The cover itself should essentially be a collection of patches, no more, and a superpoint is something I've used for my personal algorithm. 

####1. Superpoints
A superpoint is characterized by the smallest interval of a layer that contains all 16 points. By abuse of notation, we can mathematically express it either a list of 16 numbers 
$$ S = [s_1, s_2, \ldots, s_{16}] \text{ with } s_1 < s_2 < \ldots < s_{16}$$
or as the closed interval between the minimum and maximum values 
$$S = [s_1, s_{16}]$$
If we would like to see if a float value $p$ is contained within a superpoint, then we can run the `contains(p)` method, which returns a boolean describing whether $p \in [s_1, s_{16}]$. This is the basic functionality of the superpoint. 

#### 2. Patches
A patch is simply a collection of 5 superpoints. They should all be from different layers, but this check (for computational reasons) have not been implemented. Given superpoints $S_1, \ldots, S_5$, a patch $P$ is mathematically expressed as 
$$P = (S_1, S_2, S_3, S_4, S_5)$$ 
Note that this is implemented as a tuple, since there should be no further mutation of this collection. We initialize a `Patch` object by inputting a tuple of superpoints objects and the underlying environment. 
```
# assume the sp1,...,sp5 have been initialized 
sp_array = (sp1, sp2, sp3, sp4, sp5) 
patch = Patch(env, sp_array) 
``` 
This constructor actually will check that the `sp_array` contains `env.layers` superpoints. I figured that this check should be important at least for now since this is a common error. The `contains` method is very important, since this allows the user to determine if a patch contains a line. 
```
patch.contains(line) 
# returns true if patch contains line 
``` 
Remember previously that a line can be characterized by the `env.layers`=$5$ points lying on each layer. We can describe a line as 
$$l = [l_1, l_2, l_3, l_4, l_5]$$ 
with $l_i$ is the float value on the $i$th layer. We can also characterize a patch as a 5-tuple of superpoints, which are essentially closed intervals. 
$$P = ([\min{S_1}, \max{S_1}], [\min{S_2}, \max{S_2}], [\min{S_3}, \max{S_3}], [\min{S_4}, \max{S_4}], [\min{S_5}, \max{S_5}])$$ 
Therefore, the contains method $\mathcal{C}$ determines whether $l \in P$ by determining whether $l_i \in [\min{S_i}, \max{S_i}]$ for $i \in [5]$. That is 
$$\mathcal{C}(P, l) \coloneqq \begin{cases} 
\text{True} & \text{ if } l_i \in [\min{S_i}, \max{S_i}] \text{ for } i \in [5] \\
\text{False} & \text{ if else }
\end{cases}$$
This function will be clearly useful for constructing a cover and performance testing it. 


####3. Covers

A cover $C$ is essentially a list of patches. Therefore, given $n$ patches, $P_1, \ldots, P_n$, a cover is mathematically described as 
$$C = [P_1, \ldots, P_n]$$
Now it is initialized in a bit of a different way. It takes in an `Environment` object and a `DataSet` object, and constructs an empty cover first, without any patches inside. It has 5 attributes 
```
cover = Cover(env, data)
cover.n_patches             # number of patches = 0
cover.env                   # the embedding environment object
cover.data                  # the inputted DataSet object
cover.patches               # an empty list of patches
cover.superPoints           # a list of lists of superpoints
``` 
In the constructor, we do the following for each layer $i$, which contains $n$ points each. 
- We initialize a list representing the superpoints in layer $i$. 
- A superpoint is constructed by taking the first 16 points $1, \ldots, 16$ and added to this list. 
- We take points $16, \ldots, 31$ to make a second superpoint and add this to the list. Note that there is an overlap of one point between adjacent superpoints. 
- We continue this until there are less than 16 points left for the final superpoint. 
- The final superpoint is constructed by taking the last 16 points and added to the list. 
For $n = 150$, this should create $10$ superpoints for each layer, and if we have 5 layers, $cover.superPoints$ should be a list of 5 lists, each containing 10 superpoints. 

#### Attaining Estimations of the Minimal Cover 
The `solve` method of the `Cover` object is where the main algorithm resides. Now that we have a list of list of superpoints upon initialization, which we will label 
$$[[S_{1,1}, S_{1, 10}], \ldots, [S_{5,1}, S_{5, 10}]]
where $S_{i, j}$ represents the $j$th superpoint in the $i$th layer. The algorithm is run as such: 
1. We construct a `LineGenerator` object and have it generate 100 equally spaced lines in the environment. These list of lines are generated "from left to right," meaning that the line that resides in the leftmost portion is the first element of the list, and the rightmost in the last element. 
2. For the first line $l = [l_1, l_2, l_3, l_4, l_5]$, we look at $l_i$ and find which superpoint in the $i$th list of `cover.superPoints` it is contained in. After $i = 1, \ldots, 5$, we should have a collection of $5$ superpoints, which are stored in the `patch_ingredients` variable. 
3. We construct the patch $P$ from the elements of `patch_ingredients`, which is guaranteed by construction to contain line $l$ and add it to `cover.patches` (and increment `cover.n_patches` by $1$). 
4. We move onto the next line and do the same. Note that for each line, we do not need to iterate through all the superpoints. This is because we're going from left to right, and so given that line $l_k$ is contained in the patch 
$$(S_{1, 3}, S_{2, 3}, S_{3, 4}, S_{4, 2}, S_{5, 1})$$
the next line $l_{k+1}$ must be contained in the superpoint that comes at least after those of line $l_k$. Therefore, the corresponding patches must be of form 
$$(S_{1, j_1}, S_{2, j_2}, S_{3, j_3}, S_{4, j_4}, S_{5, j_5})$$
where $j_1 \geq 3, j_2 \geq 3, j_3 \geq 4, j_4 \geq 2, j_5 \geq 1$. This will save a lot of computational time by design. 

5. We repeat the above steps for all 100 lines. To detect repeated patches, unfortunately we cannot use hashsets since patches are not hashable objects (implementing this would be very nice). Therefore, for every generated patch $P_k$ for line $l_k$, we just compare it with the latest patch that is stored in `cover.n_patches`. Just this one comparison is sufficient since again, since the patches are generated from left to right, and therefore, $l_k \not\in P_{k-1} \implies l_k \not\in P_1, \ldots, P_{k-2}$. 

6. After all repetitions we have our desired cover stored in the `cover.patches` list. 