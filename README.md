# The Genomics DeepDive Project

We have a wiki for this project at
<http://dev.stanford.edu/confluence/display/collaborators/DeepDive+Genomics>

Contact Matteo Riondato <rionda@cs.stanford.edu> for information.



## Performing Labeling Tasks

We use a GUI tool called [*Mindtagger*][mindtagger] to expedite the labeling tasks necessary for evaluating the data products of DeepDive.

### 1. Launching Mindtagger

To start the GUI tool, simply run:
```bash
./labeling/start-gui.sh
```

and open a browser to "http://localhost:8000".

The GUI shows, in the upper left corner, all tasks defined under `labeling/` directory.
The results of the labeling (including intermediate data) are stored under each task directory.

### 2. How to send back your tags
Use the `push.sh` script:
```bash
./push.sh
```

It will create a commit holding any changes made on your side, and push to the [original GitHub repo](https://github.com/rionda/dd-genomics).
Enter your GitHub user name and password that has been added as a collaborator account when asked.
If you don't have a collaborator GitHub account, the script can generate a set of patch files that can be emailed to the authors instead.

We will review and merge the work, and it will help the next iteration of improving the data products.

### 3. How to grab upstream changes
Use the `pull.sh` script to grab any new tasks or changes made on the original repo:
```bash
./pull.sh
```

It will first create a commit holding any changes made on your side, and fetch and merge the updates, honoring the changes you made (read: the tags you entered).


### 4. How to create a new labeling task
Use the `labeling/create-new-task.sh` script to create new labeling tasks.


[mindtagger]: https://github.com/netj/mindbender
