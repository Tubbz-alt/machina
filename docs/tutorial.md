
# configurables (setup) and parameterizables (variants)

- instructions, exit interview
- measures
- setup: model, data, training, etc.
- UI
- explainers


## Anatomy of an Project

A project should be defined as a series of experiments that operate/share on the same data/models. In this example, the two experiments have different measures, interfaces, and tasks but they use the same underlying trained models and datasets. To ensure consistency between them (and avoiding possibly expensive retraining/processing) we can put the two experiments in the same project.

```
my_project/
    __init__.py
    setup.py
    my_experiment1/
        __init__.py
        variants/
            shap.py
            linear.py
            random.py
            lasso.py
        templates/
            layout.tmpl
            instructions.tmpl
            experiment.tmpl
            explanation.tmpl
            bars.tmpl
            exit_interview.tmpl
        experiment.py
        run.py
        measures.py
        ...
    my_experiment2/
        ...
```


## Anatomy of an Experiment

Directory structure

```
my_experiment/
    templates/
        ...
    explainers.py
```

## Projects vs. Experiments

If you are doing academic research with `machina`, a project might correspond to all the the experiments that are part of a single paper. And each experiment would be a single user study testing a single hypothesis. An important point to keep in mind is that due to the way `machina` automates experiments on MTurk, the participants are always unique *within* an experiment (i.e. each participant is restricted to only complete the experiment trial once) but between experiments there could be some duplication (a single individual can participate in each one of the experiments of a project).

For example, from a recent interpretable machine learning [paper]() that used `machina`, if you look at the Github repository containing the code for the paper you can see that the two experiments are part of a single `machina` project. 

## Anatomy of an Explainer


## Coming from Django

Project -> project
App -> experiment


* local development server has autoreload