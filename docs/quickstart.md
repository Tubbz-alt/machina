
```bash
machina new model-transparency
cd model-transparency
machina serve
#=> localhost:5555 
```

## The Trial Context

Each participant should trigger an assignment to the factors specified in a view function, and these are added to the `trial` context (analogous to the `request` context or sessions in flask). The `trial` is a special object is actually backed by a Flask `session` object and anything you write to the `trial` (as long as it is `pickle`-able) is serialized and written to the database once the experiment is completed. You can also write intermediate values to the database if you would like.

## Working with Existing Applications

Have an existing Flask application? No problem! Just use Machina as a blueprint.

```python
experiment = Machina('channel-cap', __name__, seed=18, url_prefix='/experiment')

app.register_blueprint(experiment)
```