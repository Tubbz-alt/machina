## Machina

> A familiar, full stack (yet lightweight) framework for digital experimentation, human orchestration, and interactive machine learning applications.

Machina combines an intuitive **experimentation framework** (think A/B tests) with flexible **human-in-the-loop orchestration** to support and accelerate interactive ML research with a focus on *consistency*, *reproducibility*, and *experimentation*. We make it so easy to evaluate your new algorithm with ✨real humans✨... you'd be foolish not to! 

<hr> 

Machina automates the boring stuff and stays out of your way when it comes to the fun/interesting stuff. The framework combines an intuitive Flask-like web framework, built-in deployment and devops functionality, and Mechanical Turk management/orchestration. Specifically it provides utilities for adaptive experimentation, metrics and measures, templates and UI, data storage, participant management and authorization, experiment serialization and replication, application deployment, MTurk orchestration, a monitoring/admin dashboard, and statistical analysis helpers.  

**Use machina if you want:**
* Amazon Mechanical Turk automation and human orchestration for intelligent human-in-the-loop systems
* Adaptive experimentation powered by optimal Bayesian experimental design to efficiently evaluate your ML applications
* Modular Python components for building interactive ML interfaces (which render as HTML and serialize as JSON)

**machina can help if you are a:**
* Researcher studying interpretable ML algorithms and want to benchmark against existing methods.
* Social scientist or HCI researcher evaluating XAI systems with user experiments.
* Developer building interactive machine learning interfaces and systems.
* Data scientist needing to explain, debug, and understand ML models.

**Scalable:**
* Effort: Zero configuration deployment to the cloud.. and crowd!
* Cost: Zero cost experiment hosting... so more of your budget goes to your participants
* Science: Rerun existing experiments with one command to replicate, remix, or extend!

**To get started:**
* Read the **[documentation](docs/readme.md)**!
* Check out the 👉 **[example](example)**!!

If you want to learn about our research on/with machina, all the gory details are included in the following paper: [probably an arXiv link]...

<!-- ## What magic is this?!?!

By combining concepts from the programing language community (typing systems, formal verification, and code generation) with the systems community (query optimization, data flow graphs, and ). 

For instance only certain types of model are compatible with a given explinaer or dataset. Through the automatic checking and generation of trials, the DSL can generate the optimal configuration of experiments. If two trajectries are incompatible within a single factorial experiment the framework splits them into two seperate trials. 

- need to iterate quickly, no problem. traditionally the experiment workflow is very slow. design experiment, build experiment, pilot experiemnt, tweak experiment implementation, run at scale with subjects on MTruk. But if you want to test a slight variation or compare a new manipulation or use new measures you often have to start from scratch again. need to change parameters of an experiment, this framework intelligently figures out which trials from your experiment specification need to be rerun.


## Quickstart

```python
pip install machina

# run generator to bootstrap new experiment
machina new iml-experiment
cd iml-experiment

machina 
```
-->

## Goals

More than the development gains from using the library, we feel that these abstractions we present in the framework are a beneficial way to think about human subjects experiments involving machine learning (or any complex stochastic system).

- **Interdisciplinary collaboration** for explainable AI research through model/method, data, and experiment sharing and remixing.
- **Reproducible research** through serialized experiments with standardized taks, datasets, interfaces, and measures.
- **Portability** enabling anyone anywhere to rerun your experiment on any platform with any participants.
- **Consistent** encode best practices of running ML human subjects experiments in the framework itself so you don't have to worry you checked all the boxes. (and helpful for onboarding new experimenters!)
- **Automate the boring stuff** to lower the floor and raise the ceiling of explainable AI research... allowing you to focus on what's fun and impactful.
- **Increase participation** of who is building and studying ML systems to create more accessable and equitable applications.
- **Modular design** so you can take only what you need and leave the rest.
    - Building an interactive ML application? Use the web framework and UI components (and get serilaization for free).
    - Running user experiment with an existing application? Use the experimentation utilities to design the study and assign users to variants (and get statistical bookkeeping an analysis for free).  
- **Always open, always [free](https://mako.cc/writing/hill-free_tools.html)**

## Features

- Reference implementations of common XAI explainers and state of the art methods to compare against.
- Common interpretable benchmark datasets and synthetic data generators across modalities (tabular, text, image, etc.) in a consistent data loading format.
- Standardized measures to record how humans interact with your experiment and built-in logging.
- Consistent class interfaces to enable seamless multitasking over datasets, models, and explainers making comprehensive evaluation a breeze.
- MTurk automation, experiment data logging, and hosting of results.
- Experiment serialization and versioning to snapshot experiment parameters, interfaces, and model state to facilitate reproduction or remixing.

<!-- - Experiment "compiler" to render experiment as static site — with unique hashed address "password"
- All Python. All the Time. Declarative Python components to reduce context switching and ease the development of interactive interfaces. 
- Dynamic web application creation to run experiments following the principle of convention over configuration.
- Typed classes enabling static analysis to catch errors before you run your experiment.
- Hot reloading for interactive debugging of ML applications.
- Cross language applications powered by Apache Arrow serilaization, ONNX exchange format, and PMML?
- Supports serialization of arbitrary objects, functions, and lambdas with `cloudpickle` -->

## One explainy boi
<!-- 
```python

``` -->

See the full annotated and runnable example code [here](example).

## Installation

> :warning: Compatible with Python 3.x

### Recommended

`pip install machina`

### Development/Source

```shell
git clone https://github.com/hopelessoptimism/machina.git
cd machina && python setup.py install
```

<!-- ## Quickstart

## Gotchas -->


## What's in here?!

The main functionality the library provides is a standardized set of datasets, tasks, models, and measures for ML user experiments, all accessible through a common API to enable rapid and scalable evaluation of various interpretable ML techniques. By standardizing an environment in which to conduct interpretability and [FAT](https://fatconference.org/) research, we hope to accelerate the pace and replicability of ML research that dependends on human interaction and feedback.

At a high level, `machina` can be thought of as a compiler for interpretable machine learning human subjects experiments, but instead of generating code this compiler translates your experiment specification-- datasets, models, and explainers  --into the necessary variants to evaluate. The framework outputs HTML interfaces, instruments them with measures to run your experiment with human subjects (and optionally deploys these experiments to crowdworker platforms like Amazon's Mechanical Turk).

<!-- 

### Datasets and tasks

* existing ML benchmark datasets used in other experiments
* XAI specific datasets

### Interpretable Models

* Decision Sets
* BRL

### Explainers

* black box explainers
    * LIME
    * MAPLE
    * Counterfactuals
        * works for classification and regression
        * works for categorical and continuous features
        * effiecient with gradient estimation
    

### Components

* UI
    * interactive decision tree
    * rule lists
    * saliency maps
    * image
    * text with highlights
    * Activation visualization

TODO

- combinatorial exploration of design space.
- analyze data from other experiemtns
- remote GPU integration to train models on amazon lambda
- want to rerun their experiment with your methods, just remix/fork their experiment!
- want to test their method on your experiment, remix your own experiment!

 -->
## Standing on the shoulders of giants...

- [Flask](https://palletsprojects.com/p/flask/)
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [peewee](http://docs.peewee-orm.com/en/latest/)
- [SQLite](https://www.sqlite.org/index.html)
- [numpy](https://numpy.org/)
- [pandas](https://pandas.pydata.org/)

## See Also

* [eli5](https://github.com/TeamHG-Memex/eli5)
* [iml](https://github.com/christophM/iml)
* [Skater](https://github.com/oracle/Skater)
* [What-If Tool](https://pair-code.github.io/what-if-tool/)
* [SHAP](https://github.com/slundberg/shap)
* [lime](https://github.com/marcotcr/lime)

## Feedback/Questions/Contributing

📧 [@jonathandinu](https://twitter.com/jonathandinu)

## License

[LICENSE.mit](LICENSE.mit)

## Citation

```
@software{machina,
  author = {Jonathan Dinu},
  title = {Machina: A declarative framework for efficient lifelong experiments 
  and budgeted designs for adaptive experimentation on crowd marketplaces},
  url = {https://github.com/hopelessoptimism/machina},
  version = {0.0.1},
  month = {Oct},
  year = {2019}
}
```

<!-- 
## TODO (roughly in order of priority)

### Soon

- [ ] Docker autobuild for experiments
- [ ] Experiment deploy to MTurk
   - [ ] deploy server to Amazon EC2 or ECS
   - [ ] experiment management
   - [ ] worker assignment
   - [ ] data collection/syncing

### Later

- [ ] command line interface
- [ ] Add datasets
   - [x] Inside Airbnb dataset
   - [ ] COMPAS dataset
   - [ ] Boston Housing dataset 
   - [ ] Lending Club dataset
- [ ] Add explainer reference implementations
    - [x] LIME explainer
    - [ ] MAPLE explainer
    - [ ] Saliency explainer
- [ ] Model imports examples in docs
   - [ ] sklearn
   - [ ] ONNX
- [ ] add proper type annotations for Pyre/mypy
- [ ] Statistical analysis helpers for results 
- [ ] Interface serialization with Dash
- [ ] add interactive notebooks with Binder -->