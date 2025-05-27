#!/usr/bin/env python3

from flask import Flask, render_template, send_from_directory, abort, request
import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / 'scripts'))
from repo_config import RepoConfig

app = Flask(__name__)

@app.route('/')
def index():
    """Display the main repository page."""
    distributions = []
    for dist in RepoConfig.DISTRIBUTIONS:
        dist_path = RepoConfig.get_dist_path(dist)
        if dist_path.exists():
            components = []
            for comp in RepoConfig.COMPONENTS:
                comp_path = dist_path / comp
                if comp_path.exists():
                    components.append({
                        'name': comp,
                        'path': f'{dist}/{comp}'
                    })
            distributions.append({
                'name': dist,
                'components': components
            })
    
    return render_template('index.html',
                         repo_name=RepoConfig.REPO_NAME,
                         repo_description=RepoConfig.REPO_DESCRIPTION,
                         distributions=distributions)

@app.route('/docs')
def docs():
    """Display repository documentation."""
    return render_template('docs.html',
                         repo_name=RepoConfig.REPO_NAME,
                         gpg_key_id=RepoConfig.GPG_KEY_ID)

@app.route('/dist/<distribution>/<component>')
def component_view(distribution, component):
    """Display information about a specific distribution component."""
    if distribution not in RepoConfig.DISTRIBUTIONS:
        abort(404)
    if component not in RepoConfig.COMPONENTS:
        abort(404)
    
    dist_path = RepoConfig.get_dist_path(distribution)
    comp_path = dist_path / component
    if not comp_path.exists():
        abort(404)

    # Get available architectures
    architectures = []
    for arch in RepoConfig.ARCHITECTURES:
        arch_path = comp_path / f"binary-{arch}"
        if arch_path.exists():
            architectures.append(arch)

    # Get available packages
    packages = []
    for arch in architectures:
        packages_file = comp_path / f"binary-{arch}" / "Packages"
        if packages_file.exists():
            with open(packages_file) as f:
                package_info = {}
                for line in f:
                    line = line.strip()
                    if not line and package_info:
                        packages.append(package_info)
                        package_info = {}
                    elif line:
                        key, value = line.split(": ", 1)
                        package_info[key] = value
                if package_info:
                    packages.append(package_info)

    return render_template('component.html',
                         repo_name=RepoConfig.REPO_NAME,
                         distribution=distribution,
                         component=component,
                         architectures=architectures,
                         packages=packages)

@app.route('/pool/<path:filename>')
def serve_package(filename):
    """Serve package files from the pool directory."""
    return send_from_directory(RepoConfig.POOL_DIR, filename)

@app.route('/dists/<path:filename>')
def serve_dist_file(filename):
    """Serve distribution files (Release, Packages.gz, etc.)."""
    return send_from_directory(RepoConfig.DISTS_DIR, filename)

@app.route('/key.gpg')
def serve_key():
    """Serve the repository's GPG key."""
    return send_from_directory(app.static_folder, 'key.gpg')

if __name__ == '__main__':
    app.run(host=RepoConfig.WEB_HOST, port=RepoConfig.WEB_PORT, debug=True)
