
* `machina new`
* `machina destroy [experiment name]`
* `machina register experiment.py`
* `machina generate explainer Shap`
* `machina serve --debug`
* `machina containerize`
* `machina deploy {--public | --aws | --heroku}`
* `machina ping` (or status)
* `machina run --sandbox`
* `machina progress`
* `machina extend 50`
* `machina shutdown`

* `machina fetch/sync`
* `machina connect -N` ssh to machine. ssh tunnel? or DB client.
* `machina database`
* `machina dashboard`
* `machina export results.csv`

* `machina freeze`
* `machina hydrate experiment.db`

* `machina remix http://github.com/...`


- [ ] machina new …
- [ ] machina scaffold pairwise
- [ ] machina scaffold prediction
- [ ] machina scaffold sequential
- [ ] machina add measure confidence
- [ ] machina add measure timer
- [ ] machina add measure pairwise
- [ ] machina deploy --gunicorn wsgi.py
- [ ] machina clone https://github….
- [ ] machina remix https://github…
- [ ] machina replicate https://github…
- [ ] machina publish .


## `machina new`

## `machina serve`

`-d --debug`

`-p --port`

## `machina generate`

* Explainer
* Dataset
* Measure
* ...

## `machina progress`

Prints out:
* total assignments
* number of assignments completed
* number of orphaned assignments -- and need to be reassigned
* number of active assignments
* ave. time per assignment

