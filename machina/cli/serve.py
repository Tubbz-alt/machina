import os, subprocess, argparse, multiprocessing

cores = multiprocessing.cpu_count()

def serve(path, variable_name, host, port, debug, worker_class, worker_connections, workers, threads, preload_off, config, profile, https, target):
    run_args = [
        'gunicorn',
        '-k', worker_class,
        '--worker-connections', str(worker_connections),
        '-w', str(workers),
        '--threads', str(threads),
        '-b', host + ':' + str(port),
        '-n', f'machina-experiment-server',
        '--env', f"TARGET={target}"
    ]

    if config:
        run_args += ['-c', config]

    if not preload_off:
        run_args += ['--preload']

    if https:
        run_args += ['--env', 'SESSION_COOKIE_SECURE=1']

    app_path = os.path.abspath(path)
    app_dir = os.path.dirname(app_path)
    app_mod = os.path.splitext(os.path.basename(app_path))[0]

    run_args += ['--chdir', f'{app_dir}', f'{app_mod}:{variable_name}.app']

    return subprocess.run(run_args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run experiment application server. Suitable for deployments.')
    parser.add_argument('path', type=str, help='Path to experiment file.')
    parser.add_argument('-n', '--name', type=str, default='experiment', help='Name of experiment variable which wraps Flask app.')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Hostname address to run experiment.')
    parser.add_argument('-p', '--port', type=int, default=5001, help='Server port to run experiment.')
    parser.add_argument('--worker_class', type=str, default='gevent', help='The type of workers to use.')
    parser.add_argument('--worker_connections', type=int, default=99, help='The maximum number of simultaneous clients. This setting only affects the Eventlet and Gevent worker types.')
    parser.add_argument('-w', '--workers', type=int, default=2*cores + 1, help='Number of worker processes to use.')
    parser.add_argument('--threads', type=int, default=1, help='Number of threads per worker')
    parser.add_argument('-c', '--config', type=str, help='Path to gunicorn configuration file.')
    parser.add_argument('--https', action="store_true", help='Serve over HTTPS')
    parser.add_argument('-t', '--target', type=str, default='local', help='Submit results to worker Sandbox')
    parser.add_argument('--debug', action="store_true", help='Debug flag.')
    parser.add_argument('--profile', action="store_true", help='Profile flag.')
    parser.add_argument('--preload_off', action="store_true", help='Turn off gunicorn application preloading.')

    args = parser.parse_args()
    
    serve(path=args.path, 
          variable_name=args.name, 
          host=args.host, 
          port=args.port, 
          debug=args.debug, 
          worker_class=args.worker_class,
          worker_connections=args.worker_connections,
          workers=args.workers, 
          threads=args.threads,
          preload_off=args.preload_off, 
          config=args.config, 
          profile=args.profile,
          https=args.https,
          target=args.target)