# Debian-HPC Repository Documentation

## Project Overview

This project implements a Debian-style package repository system designed for High Performance Computing (HPC) packages. It provides a complete infrastructure for hosting, managing, and distributing Debian packages with proper security measures and a web interface.

## Repository Structure

```
debian-hpc/
├── dists/                  # Distribution metadata and indices
│   ├── stable/            # Stable distribution
│   │   ├── main/         # Main component
│   │   ├── contrib/      # Contrib component
│   │   ├── non-free/     # Non-free component
│   │   ├── Release       # Release file
│   │   ├── Release.gpg   # GPG signature for Release
│   │   └── InRelease     # Inline signed Release
│   └── testing/          # Testing distribution (same structure as stable)
├── pool/                  # Package storage
│   ├── main/             # Main component packages
│   ├── contrib/          # Contrib component packages
│   └── non-free/         # Non-free component packages
├── scripts/              # Repository management scripts
├── web/                  # Web interface
├── logs/                 # Log files
└── manage.py            # Main management script
```

## Core Components

### 1. Repository Configuration (scripts/repo_config.py)

```python
#!/usr/bin/env python3

import os
from pathlib import Path

class RepoConfig:
    # Repository Information
    REPO_NAME = "debian-hpc"
    REPO_DESCRIPTION = "High Performance Computing Debian Repository"
    REPO_VERSION = "1.0.0"

    # Repository Structure
    DISTRIBUTIONS = ["stable", "testing"]
    COMPONENTS = ["main", "contrib", "non-free"]
    ARCHITECTURES = ["amd64", "i386"]

    # GPG Configuration
    GPG_KEY_ID = "D8D87602D00F0680F44BD468F90FBC2AE63EB38F"
    GPG_SIGNING_USER = "Nishanth <nishanthc264@gmail.com>"

    # Web Interface Configuration
    WEB_HOST = "localhost"
    WEB_PORT = 8080
    WEB_TITLE = "debian-hpc Repository"

    # Paths
    BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    POOL_DIR = BASE_DIR / "pool"
    DISTS_DIR = BASE_DIR / "dists"
    WEB_DIR = BASE_DIR / "web"
    LOG_DIR = BASE_DIR / "logs"

    # Create required directories
    LOG_DIR.mkdir(exist_ok=True)

    # Logging Configuration
    LOG_FILE = LOG_DIR / "repo.log"
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Package validation settings
    REQUIRED_FIELDS = [
        "Package",
        "Version",
        "Architecture",
        "Maintainer",
        "Description"
    ]
```

### 2. Package Manager (scripts/repo_manager.py)

This script handles package management, including:
- Adding packages to the repository
- Generating package indices
- Updating repository metadata

Key features:
- Package verification
- Automatic index generation
- Checksum calculation
- Component management

### 3. GPG Signing (scripts/repo_sign.py)

Handles all GPG signing operations:
- Package signing
- Release file signing
- Key management

### 4. Web Interface (web/app.py)

Flask-based web interface providing:
- Repository browsing
- Package listing
- Documentation
- Installation instructions

## Usage Instructions

### 1. Initialize Repository

```bash
./manage.py init
```

This creates the basic repository structure and initializes GPG signing.

### 2. Add Packages

```bash
./manage.py add-package path/to/package.deb stable main
```

### 3. Update Repository Indices

```bash
./manage.py update
```

### 4. Start Web Interface

```bash
cd web && python3 app.py
```

## Client Setup

To use the repository:

1. Add GPG key:
```bash
wget -qO - http://your-server/key.gpg | sudo apt-key add -
```

2. Add repository:
```bash
echo "deb [signed-by=/usr/share/keyrings/debian-hpc.gpg] http://your-server stable main" | \
    sudo tee /etc/apt/sources.list.d/debian-hpc.list
```

3. Update and install:
```bash
sudo apt update
sudo apt install package-name
```

## Security Considerations

1. GPG Signing
   - All packages are signed
   - Release files are signed
   - InRelease files for secure apt

2. File Permissions
   - Pool directory: read-only for users
   - GPG keys: protected
   - Log files: restricted access

## Creating Test Packages

The repository includes a test package creation script:

```bash
./scripts/create_test_package.py package-name version "description"
```

Example:
```bash
./scripts/create_test_package.py hpc-test 1.0.0 "Test package for HPC repository"
```

## File Descriptions

### Web Interface Templates

1. base.html - Base template with common layout
2. index.html - Homepage with repository overview
3. distribution.html - Distribution-specific information
4. component.html - Component package listing
5. docs.html - Repository documentation

### Management Scripts

1. manage.py - Main management interface
2. repo_manager.py - Package and repository management
3. repo_sign.py - GPG signing operations
4. repo_config.py - Configuration settings

## Development Guidelines

1. Package Naming
   - Follow Debian naming conventions
   - Use proper version numbering
   - Include architecture information

2. Component Guidelines
   - main: Free software packages
   - contrib: Free software depending on non-free
   - non-free: Non-free software

3. Testing Procedures
   - Verify package builds
   - Check signatures
   - Validate metadata
   - Test installation

## Maintenance Tasks

1. Regular Updates
   - Update package indices
   - Verify signatures
   - Check log files
   - Backup repository data

2. Security Updates
   - Monitor GPG key expiration
   - Update signing keys
   - Check package signatures
   - Review access logs

## Troubleshooting

1. Package Installation Issues
   - Verify GPG key installation
   - Check repository configuration
   - Validate package signatures
   - Review apt update output

2. Repository Updates
   - Check log files
   - Verify file permissions
   - Validate index generation
   - Test package installation

## Future Improvements

1. Features to Add
   - Package search functionality
   - User authentication
   - Package statistics
   - Automated testing

2. Security Enhancements
   - HTTPS support
   - Access control
   - Audit logging
   - Backup system


## Installation and Setup Guide

### System Requirements

1. Operating System
   - Debian/Ubuntu-based Linux distribution
   - Tested on Debian 12 (Bookworm)

2. Required Packages
```bash
# Core dependencies
sudo apt-get install \
    python3 \
    python3-flask \
    dpkg-dev \
    gnupg2 \
    apache2

# Development tools
sudo apt-get install \
    devscripts \
    build-essential \
    debhelper
```

### Initial Setup

1. Clone the Repository
```bash
git clone https://github.com/yourusername/debian-hpc.git
cd debian-hpc
```

2. Create Directory Structure
```bash
mkdir -p \
    pool/{main,contrib,non-free} \
    dists/{stable,testing}/{main,contrib,non-free}/{binary-amd64,binary-i386,source} \
    web/{templates,static/css} \
    scripts \
    logs
```

3. Configure GPG
```bash
# If you don't have a GPG key:
gpg --full-generate-key

# Export your public key
gpg --armor --export YOUR_KEY_ID > web/static/key.gpg
```

4. Update Configuration
Edit `scripts/repo_config.py` to set:
- Your GPG key ID
- Repository name and description
- Web interface settings

### Setting Up Apache (Production)

1. Create Apache Configuration
```bash
sudo nano /etc/apache2/sites-available/debian-hpc.conf
```

Add:
```apache
<VirtualHost *:80>
    ServerName your-repo-server
    DocumentRoot /path/to/debian-hpc/web

    WSGIDaemonProcess debian-hpc python-path=/path/to/debian-hpc
    WSGIScriptAlias / /path/to/debian-hpc/web/wsgi.py

    <Directory /path/to/debian-hpc/web>
        WSGIProcessGroup debian-hpc
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>

    Alias /pool /path/to/debian-hpc/pool
    Alias /dists /path/to/debian-hpc/dists
    
    <Directory /path/to/debian-hpc/pool>
        Options Indexes FollowSymLinks
        Require all granted
    </Directory>

    <Directory /path/to/debian-hpc/dists>
        Options Indexes FollowSymLinks
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/debian-hpc-error.log
    CustomLog ${APACHE_LOG_DIR}/debian-hpc-access.log combined
</VirtualHost>
```

2. Enable the Site
```bash
sudo a2ensite debian-hpc
sudo systemctl reload apache2
```

### Creating Your First Package

1. Create a Test Package
```bash
cd scripts
./create_test_package.py hpc-test 1.0.0 "Test package for HPC repository"
```

2. Add the Package to Repository
```bash
cd ..
./manage.py add-package scripts/hpc-test_1.0.0_all.deb stable main
```

3. Update Repository Indices
```bash
./manage.py update
```

### Verification Steps

1. Check Repository Structure
```bash
tree dists/ pool/
```

2. Verify Package Signing
```bash
gpg --verify dists/stable/Release.gpg dists/stable/Release
```

3. Test Package Installation
```bash
# Add repository
echo "deb [signed-by=/usr/share/keyrings/debian-hpc.gpg] http://localhost stable main" | \
    sudo tee /etc/apt/sources.list.d/debian-hpc.list

# Add GPG key
wget -qO - http://localhost/key.gpg | sudo apt-key add -

# Update and install
sudo apt update
sudo apt install hpc-test
```

### Backup and Maintenance

1. Regular Backups
```bash
# Backup script (create as backup.sh)
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d)
tar czf "$BACKUP_DIR/debian-hpc-$DATE.tar.gz" \
    pool/ \
    dists/ \
    web/ \
    scripts/ \
    logs/ \
    *.py \
    *.md
```

2. Log Rotation
Add to /etc/logrotate.d/debian-hpc:
```
/path/to/debian-hpc/logs/*.log {
    weekly
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    create 640 root adm
}
```


## Development Guide

### Common Development Tasks

#### 1. Adding a New Package Type

To add support for a new type of package:

1. Update Package Builder
```python
# In scripts/create_test_package.py

def create_specialized_package(name, version, description, package_type):
    """Create a specialized package type."""
    with tempfile.TemporaryDirectory() as temp_dir:
        package_dir = Path(temp_dir) / f"{name}-{version}"
        debian_dir = package_dir / "debian"
        os.makedirs(debian_dir)

        # Add specialized dependencies
        dependencies = get_package_dependencies(package_type)
        
        # Create control file with specialized fields
        create_control_file(debian_dir, name, version, description, dependencies)
        
        # Add package-specific files
        add_package_files(package_dir, package_type)
        
        # Build the package
        build_package(package_dir)
```

2. Add Package Validation
```python
# In scripts/repo_manager.py

def validate_package(self, package_path, package_type):
    """Validate package based on type."""
    try:
        # Basic validation
        if not self._verify_package(package_path):
            return False
            
        # Type-specific validation
        if not self._verify_package_type(package_path, package_type):
            return False
            
        return True
    except Exception as e:
        self.logger.error(f"Package validation failed: {e}")
        return False
```

#### 2. Implementing New Web Features

1. Add New Route
```python
# In web/app.py

@app.route('/packages/search')
def search_packages():
    """Search packages in the repository."""
    query = request.args.get('q', '')
    results = search_repository(query)
    return render_template('search.html', 
                         results=results,
                         query=query)
```

2. Create Template
```html
<!-- In web/templates/search.html -->
{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1>Search Results</h1>
        <form class="mb-4">
            <div class="input-group">
                <input type="text" class="form-control" 
                       name="q" value="{{ query }}"
                       placeholder="Search packages...">
                <button class="btn btn-primary">Search</button>
            </div>
        </form>
        
        {% if results %}
        <div class="list-group">
            {% for package in results %}
            <div class="list-group-item">
                <h5>{{ package.name }} ({{ package.version }})</h5>
                <p>{{ package.description }}</p>
                <small>Component: {{ package.component }}</small>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p>No packages found matching your query.</p>
        {% endif %}
    </div>
</div>
{% endblock %}
```

### Troubleshooting Guide

#### Common Issues and Solutions

1. Package Building Failures
```bash
# Issue: dpkg-buildpackage fails
# Solution: Check build dependencies
sudo apt-get build-dep ./package-name
# or
sudo apt-get install -y $(grep Build-Depends debian/control | sed 's/Build-Depends://g' | sed 's/,//g')
```

2. GPG Signing Issues
```bash
# Issue: GPG key not found
# Solution: List and verify keys
gpg --list-secret-keys
# Export and reimport if necessary
gpg --export-secret-keys YOUR_KEY_ID > private.gpg
gpg --import private.gpg
```

3. Repository Index Issues
```bash
# Issue: Packages file not updating
# Solution: Manually regenerate indices
cd dists/stable/main/binary-amd64/
dpkg-scanpackages . /dev/null > Packages
gzip -k -f Packages
# Then update Release file
cd ../../..
apt-ftparchive release . > Release
```

4. Web Interface Problems
```bash
# Issue: 500 Internal Server Error
# Solution: Check logs
tail -f logs/repo.log
# Check Flask debug mode
export FLASK_DEBUG=1
python3 web/app.py
```

#### Debugging Tools

1. Package Investigation
```bash
# Examine package contents
dpkg -c package.deb

# Extract package
dpkg-deb -R package.deb extracted/

# View package info
dpkg -I package.deb
```

2. Repository Verification
```bash
# Verify package indices
apt-ftparchive verify dists/stable/main/binary-amd64/Packages

# Test repository locally
apt-get update -o Dir::Etc::sourcelist="sources.list.d/debian-hpc.list" \
               -o Dir::Etc::sourceparts="-" \
               -o APT::Get::List-Cleanup="0"
```

3. GPG Verification
```bash
# Verify Release file signature
gpg --verify dists/stable/Release.gpg dists/stable/Release

# Verify package signature
gpg --verify package.deb.asc package.deb
```

### Performance Optimization

1. Apache Configuration
```apache
# Add to Apache configuration
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType application/x-debian-package "access plus 1 hour"
    ExpiresByType text/plain "access plus 5 minutes"
</IfModule>

<IfModule mod_headers.c>
    Header set Cache-Control "public, must-revalidate"
</IfModule>
```

2. Repository Optimization
```bash
# Compress package lists efficiently
find . -name Packages -exec gzip -9 {} \;

# Create package indices with optimization
apt-ftparchive -o APT::FTPArchive::AlwaysStat=false \
               -o APT::FTPArchive::PackagesOnly=true \
               packages pool > Packages
```

3. Web Interface Caching
```python
# In web/app.py
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

@app.route('/dist/<distribution>')
@cache.cached(timeout=300)  # Cache for 5 minutes
def distribution(distribution):
    # ... distribution view code ...
```

