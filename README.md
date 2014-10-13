# The Genomics DeepDive Project

We have a wiki for this project at
<http://dev.stanford.edu/confluence/display/collaborators/DeepDive+Genomics>

Contact Matteo Riondato <rionda@cs.stanford.edu> for information.



## Performing Labeling Tasks

We use a GUI tool called [*Mindtagger*][mindtagger] to expedite the labeling tasks necessary for evaluating the data products of DeepDive.

### Launching Mindtagger

To start the tool, simply run:
```bash
./labeling-tool.sh
```

It shows all tasks defined under `labeling/` directory.
The results of labeling (including intermediate ones) will reside under each task directory.

### How to send back your tags
Please use the following steps to communicate back the results, assuming you cloned from a fork.

1. From the root of this repository, commit your work to git by running:
    
    ```bash
    git add labeling/
    git commit -m 'Finished labeling 20141013-precision'
    ```
2. Then, push it to a new branch of your GitHub clone repo:
    
    ```bash
    git push origin HEAD:20141013-precision
    ```
3. Finally, go to the [original GitHub repo](https://github.com/rionda/dd-genomics), and [create a *Pull Request*](https://github.com/rionda/dd-genomics/pulls) with the branch you just pushed to.
4. We will merge the work and will be able to use it for the next iteration of improving the data products.

[mindtagger]: https://github.com/netj/mindbender
