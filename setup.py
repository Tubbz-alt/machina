from setuptools import find_packages, setup

setup(
    name='machina',
    version='0.0.1',
    description="Framework for reproducible and scalable human evaluation of interpretable machine learning systems.",
    author='Jonathan Dinu',
    author_email='jondinu@gmail.com',
    platforms=['any'],
    license="MIT",
    url='https://github.com/hopelessoptimism/machina',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'boto3',
        'gunicorn',
        'gevent',
        'flask>=1',
        'requests',
        'altair',
        'peewee',
        'pandas',
        'psycopg2'
    ]
)
