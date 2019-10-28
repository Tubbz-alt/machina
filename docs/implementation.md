`machina` is implemented as a Django app utilizing class based views and shared models to realize its goal of convention over configuration for machine learning field experiments.

## Why `machina`, why anything at all

If you don't need it, don't use it. 


## Why Django
 
Progressive enhancement and modularity. You can use as much or as little of `machina` as you want and need. Need a lightweight experimentation framework for handling and storing variant assignments? Need MTurk automation and monitoring to orchastrate your app with real people? 


## How's does it compare

TLDR; It's like a lightweight Plaout/Ax + psiTurk focused on human-in-the-loop machine learning applications.

### psiturk

* `machina` has built in experimentation (think A/B testing), `psiturk` does not.
* `psiturk` experiments are created using their javascript API.
* `machina` focused on developer productivity when creating new ML experiments with its generators, templates, etc.
* `psiturk` really just focused on MTurk deployment/management and experiment sharing.

### parlai

### PlanOut and Ax


## Architecture

### SQLite

* portable -- can share an experiment by sending a single file.
* mature 
* relational
