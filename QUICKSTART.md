# Quick Start Guide

This guide demonstrates the basic usage of the debian-hpc repository system.

## 1. Initialize the Repository

```bash
# Initialize repository structure
./manage.py init
```

## 2. Create and Add a Test Package

```bash
# Create a test package
cd scripts
./create_test_package.py my-test-pkg 1.0.0 "Test HPC package"
cd ..

# Add the package to the repository
./manage.py add-package scripts/my-test-pkg_1.0.0_all.deb stable main
```

## 3. Start the Web Interface

```bash
cd web
python3 app.py
```

## 4. Use the Repository

Add the repository to your system:

```bash
# Add GPG key
wget -qO - http://localhost:8080/key.gpg | sudo apt-key add -

# Add repository source
echo "deb [signed-by=/usr/share/keyrings/debian-hpc.gpg] http://localhost:8080 stable main" | \
    sudo tee /etc/apt/sources.list.d/debian-hpc.list

# Update and install
sudo apt update
sudo apt install my-test-pkg
```

## Code Example: Adding a Package Programmatically

```python
from repo_config import RepoConfig
from repo_manager import DebianRepoManager
from repo_sign import RepoSigner

# Initialize components
repo_manager = DebianRepoManager(RepoConfig.BASE_DIR)
signer = RepoSigner()

# Add and sign a package
package_path = "path/to/package.deb"
distribution = "stable"
component = "main"

# Add to repository
if repo_manager.add_package(package_path, distribution, component):
    # Sign the package
    signer.sign_package(package_path)
    # Update and sign repository metadata
    repo_manager.update_indices(distribution)
    signer.sign_release(distribution)
```

## Common Operations

1. Update Repository Indices:
```bash
./manage.py update
```

2. Add a Package to Testing:
```bash
./manage.py add-package package.deb testing main
```

3. Export GPG Key:
```bash
cd scripts
./repo_sign.py export-key
```

## Directory Structure Overview

```
debian-hpc/
├── dists/                  # Distribution metadata
│   ├── stable/            # Stable distribution
│   └── testing/           # Testing distribution
├── pool/                  # Package storage
│   ├── main/
│   ├── contrib/
│   └── non-free/
├── scripts/              # Management scripts
├── web/                 # Web interface
└── manage.py           # Main management script
```

## Logging and Debugging

Logs are stored in:
- `logs/repo.log`: Main repository operations
- `web/access.log`: Web interface access log
- `web/error.log`: Web interface error log

To enable debug logging:
```bash
export REPO_LOG_LEVEL=DEBUG
./manage.py <command>
```

## Common Issues and Solutions

1. GPG Signing Fails:
```bash
# Verify GPG key
gpg --list-secret-keys

# Export and reimport if needed
gpg --export-secret-keys YOUR_KEY_ID > backup.gpg
gpg --import backup.gpg
```

2. Package Addition Fails:
```bash
# Check package validity
dpkg-deb -I package.deb

# Verify permissions
ls -l pool/main/
```

3. Web Interface Issues:
```bash
# Check Flask logs
cd web
FLASK_DEBUG=1 python3 app.py
```

For more detailed information, refer to the full documentation in DOCUMENTATION.md.
