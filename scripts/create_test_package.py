#!/usr/bin/env python3
"""
Test Package Creation Module

This module provides functionality for creating test Debian packages.
It's primarily used for testing the repository system and demonstrating
package creation and management features.

The module creates a simple Debian package with basic executable content
and proper metadata, suitable for testing repository operations.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

def create_test_package(name, version, description):
    """
    Create a test Debian package with given specifications.
    
    This function creates a complete Debian package including:
    - Basic executable file
    - Package metadata (control file)
    - Copyright information
    - Changelog
    - Build system configuration
    
    Args:
        name (str): Name of the package
        version (str): Version string for the package
        description (str): Package description
        
    Returns:
        bool: True if package creation was successful, False otherwise
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create package directory structure
        package_dir = Path(temp_dir) / f"{name}-{version}"
        debian_dir = package_dir / "debian"
        os.makedirs(debian_dir)

        try:
            # Create executable content
            _create_executable(package_dir, name, version)
            
            # Create debian control files
            _create_control_file(debian_dir, name, version, description)
            _create_changelog(debian_dir, name, version)
            _create_copyright(debian_dir)
            _create_rules(debian_dir, name)
            
            # Build the package
            return _build_package(package_dir, temp_dir, name, version)
            
        except Exception as e:
            print(f"Failed to create package: {e}", file=sys.stderr)
            return False

def _create_executable(package_dir, name, version):
    """
    Create a simple executable file for the test package.
    
    Args:
        package_dir (Path): Root directory of the package
        name (str): Name of the package/executable
        version (str): Version string
    """
    bin_dir = package_dir / "usr" / "bin"
    os.makedirs(bin_dir)
    
    # Create a simple shell script
    with open(bin_dir / name, "w") as f:
        f.write(f"""#!/bin/bash
echo "This is {name} version {version}"
""")
    # Make the script executable
    os.chmod(bin_dir / name, 0o755)

def _create_control_file(debian_dir, name, version, description):
    """
    Create the debian/control file with package metadata.
    
    Args:
        debian_dir (Path): Debian directory path
        name (str): Package name
        version (str): Package version
        description (str): Package description
    """
    with open(debian_dir / "control", "w") as f:
        f.write(f"""Source: {name}
Section: science
Priority: optional
Maintainer: Repository Administrator <admin@debian-hpc.local>
Build-Depends: debhelper-compat (= 13)

Package: {name}
Architecture: all
Depends: ${{misc:Depends}}
Description: {description}
 This is a test package for the debian-hpc repository.
 .
 Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")

def _create_changelog(debian_dir, name, version):
    """
    Create the debian/changelog file.
    
    Args:
        debian_dir (Path): Debian directory path
        name (str): Package name
        version (str): Package version
    """
    with open(debian_dir / "changelog", "w") as f:
        f.write(f"""{name} ({version}) stable; urgency=low

  * Test package for debian-hpc repository

 -- Repository Administrator <admin@debian-hpc.local>  {datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}
""")

def _create_copyright(debian_dir):
    """
    Create the debian/copyright file.
    
    Args:
        debian_dir (Path): Debian directory path
    """
    with open(debian_dir / "copyright", "w") as f:
        f.write("""Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Source: https://github.com/yourusername/debian-hpc

Files: *
Copyright: 2025 Repository Administrator <admin@debian-hpc.local>
License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
""")

def _create_rules(debian_dir, name):
    """
    Create the debian/rules file with build instructions.
    
    Args:
        debian_dir (Path): Debian directory path
        name (str): Package name
    """
    with open(debian_dir / "rules", "w") as f:
        f.write(f"""#!/usr/bin/make -f
%:
	dh $@

override_dh_auto_install:
	install -D -m 755 usr/bin/{name} debian/{name}/usr/bin/{name}
""")
    # Make rules file executable
    os.chmod(debian_dir / "rules", 0o755)

def _build_package(package_dir, temp_dir, name, version):
    """
    Build the Debian package using dpkg-buildpackage.
    
    Args:
        package_dir (Path): Package source directory
        temp_dir (str): Temporary directory path
        name (str): Package name
        version (str): Package version
        
    Returns:
        bool: True if build was successful, False otherwise
    """
    try:
        # Build the package without signing
        subprocess.run(
            ["dpkg-buildpackage", "-us", "-uc", "-b"],
            cwd=package_dir,
            check=True
        )
        
        # Move the built package to the current directory
        deb_file = f"{name}_{version}_all.deb"
        shutil.move(Path(temp_dir) / deb_file, deb_file)
        print(f"Successfully created package: {deb_file}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to build package: {e}", file=sys.stderr)
        return False

def main():
    """
    Main entry point for command-line usage.
    
    Usage:
        create_test_package.py <package_name> <version> <description>
    
    Example:
        create_test_package.py hpc-test 1.0.0 "Test package for HPC repository"
    """
    if len(sys.argv) != 4:
        print("Usage: create_test_package.py <package_name> <version> <description>")
        sys.exit(1)

    name = sys.argv[1]
    version = sys.argv[2]
    description = sys.argv[3]

    success = create_test_package(name, version, description)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
