#!/usr/bin/env python3
"""
Repository Manager Module

This module provides the core functionality for managing a Debian-style package repository.
It handles package addition, index generation, and repository maintenance tasks.

The DebianRepoManager class encapsulates all repository management operations, including:
- Package validation and addition
- Repository index generation
- Package pool management
- Metadata file maintenance
"""

import os
import sys
import logging
import subprocess
import hashlib
import gzip
from datetime import datetime
from pathlib import Path

class DebianRepoManager:
    """
    Debian Repository Manager Class
    
    This class provides methods for managing a Debian package repository,
    including package management, index generation, and repository maintenance.
    
    Attributes:
        repo_root (Path): Root directory of the repository
        pool_dir (Path): Directory for storing package files
        dists_dir (Path): Directory for distribution metadata
        logger (Logger): Logging instance for the manager
    """

    def __init__(self, repo_root):
        """
        Initialize the repository manager.
        
        Args:
            repo_root (str or Path): Path to the repository root directory
        """
        self.repo_root = Path(repo_root)
        self.pool_dir = self.repo_root / 'pool'
        self.dists_dir = self.repo_root / 'dists'
        self.setup_logging()

    def setup_logging(self):
        """
        Configure logging for the repository manager.
        
        Sets up logging to both file and console with appropriate format and level.
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('repo_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('RepoManager')

    def _generate_packages_gz(self, dist_path, component, arch):
        """
        Generate Packages and Packages.gz files for a component.
        
        Args:
            dist_path (Path): Path to the distribution directory
            component (str): Component name (main, contrib, non-free)
            arch (str): Architecture (amd64, i386)
            
        Returns:
            tuple: Paths to the generated Packages and Packages.gz files
        """
        packages_dir = dist_path / component / f"binary-{arch}"
        packages_dir.mkdir(parents=True, exist_ok=True)
        packages_file = packages_dir / "Packages"
        packages_gz_file = packages_dir / "Packages.gz"

        # Find all .deb files in the pool for this component
        pool_component_dir = self.pool_dir / component
        if not pool_component_dir.exists():
            return

        # Generate Packages file content
        with open(packages_file, 'w') as f:
            for deb in pool_component_dir.glob('*.deb'):
                # Get package info using dpkg-deb
                cmd = ['dpkg-deb', '-I', str(deb)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    continue

                # Write package information
                f.write(f"Package: {deb.stem.split('_')[0]}\n")
                f.write(f"Version: {deb.stem.split('_')[1]}\n")
                f.write(f"Architecture: {arch}\n")
                f.write(f"Filename: pool/{component}/{deb.name}\n")
                
                # Calculate checksums
                with open(deb, 'rb') as deb_file:
                    content = deb_file.read()
                    f.write(f"Size: {len(content)}\n")
                    f.write(f"MD5sum: {hashlib.md5(content).hexdigest()}\n")
                    f.write(f"SHA256: {hashlib.sha256(content).hexdigest()}\n")
                
                f.write("\n")

        # Create gzipped version
        with open(packages_file, 'rb') as f_in:
            with gzip.open(packages_gz_file, 'wb') as f_out:
                f_out.write(f_in.read())

        return packages_file, packages_gz_file

    def _generate_release_file(self, dist_path, distribution):
        """
        Generate Release file for a distribution.
        
        Args:
            dist_path (Path): Path to the distribution directory
            distribution (str): Distribution name (stable, testing)
            
        Returns:
            Path: Path to the generated Release file
        """
        release_file = dist_path / "Release"

        with open(release_file, 'w') as f:
            # Write basic repository information
            f.write(f"Origin: debian-hpc\n")
            f.write(f"Label: debian-hpc\n")
            f.write(f"Suite: {distribution}\n")
            f.write(f"Codename: {distribution}\n")
            f.write(f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S UTC')}\n")
            f.write(f"Architectures: amd64 i386\n")
            f.write(f"Components: main contrib non-free\n")
            f.write(f"Description: Debian HPC Repository\n")
            
            # Add checksums section
            f.write("MD5Sum:\n")
            f.write("SHA256:\n")

            # Generate checksums for all component files
            for component in ['main', 'contrib', 'non-free']:
                for arch in ['amd64', 'i386']:
                    packages_dir = dist_path / component / f"binary-{arch}"
                    if not packages_dir.exists():
                        continue

                    # Process Packages file
                    packages = packages_dir / "Packages"
                    if packages.exists():
                        self._add_file_checksums(f, packages, component, arch)

                    # Process Packages.gz file
                    packages_gz = packages_dir / "Packages.gz"
                    if packages_gz.exists():
                        self._add_file_checksums(f, packages_gz, component, arch)

        return release_file

    def _add_file_checksums(self, release_file, file_path, component, arch):
        """
        Add checksums for a file to the Release file.
        
        Args:
            release_file (file): Open Release file handle
            file_path (Path): Path to the file to checksum
            component (str): Component name
            arch (str): Architecture name
        """
        with open(file_path, 'rb') as f:
            content = f.read()
            size = len(content)
            md5sum = hashlib.md5(content).hexdigest()
            sha256 = hashlib.sha256(content).hexdigest()
            rel_path = f"{component}/binary-{arch}/{file_path.name}"
            release_file.write(f" {md5sum} {size} {rel_path}\n")
            release_file.write(f" {sha256} {size} {rel_path}\n")

    def add_package(self, package_path, distribution, component):
        """
        Add a package to the repository.
        
        Args:
            package_path (str): Path to the .deb package file
            distribution (str): Target distribution (stable, testing)
            component (str): Target component (main, contrib, non-free)
            
        Returns:
            bool: True if package was added successfully, False otherwise
        """
        try:
            # Verify package
            if not self._verify_package(package_path):
                raise ValueError("Invalid package file")

            # Copy to pool
            dest = self._copy_to_pool(package_path, component)
            self.logger.info(f"Package added to pool: {dest}")

            # Update indices
            self.update_indices(distribution, component)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to add package: {e}")
            return False

    def _verify_package(self, package_path):
        """
        Verify debian package validity.
        
        Args:
            package_path (str): Path to the .deb package file
            
        Returns:
            bool: True if package is valid, False otherwise
        """
        try:
            result = subprocess.run(['dpkg-deb', '-I', package_path],
                                 capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Package verification failed: {e}")
            return False

    def _copy_to_pool(self, package_path, component):
        """
        Copy package to pool directory.
        
        Args:
            package_path (str): Path to the package file
            component (str): Target component
            
        Returns:
            Path: Destination path in the pool
        """
        src = Path(package_path)
        dest = self.pool_dir / component / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(src, dest)
        return dest

    def update_indices(self, distribution, component=None):
        """
        Update repository indices.
        
        Args:
            distribution (str): Distribution to update
            component (str, optional): Specific component to update. If None, updates all components.
        """
        self.logger.info(f"Updating indices for {distribution}/{component if component else 'all'}")
        
        dist_path = self.dists_dir / distribution
        dist_path.mkdir(parents=True, exist_ok=True)

        components = [component] if component else ['main', 'contrib', 'non-free']
        
        # Generate Packages files for each component and architecture
        for comp in components:
            for arch in ['amd64', 'i386']:
                self._generate_packages_gz(dist_path, comp, arch)

        # Generate Release file
        self._generate_release_file(dist_path, distribution)

def main():
    """
    Main entry point for command-line usage.
    """
    if len(sys.argv) < 2:
        print("Usage: repo_manager.py <command> [args...]")
        sys.exit(1)

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manager = DebianRepoManager(repo_root)

    command = sys.argv[1]
    if command == "add-package":
        if len(sys.argv) != 5:
            print("Usage: repo_manager.py add-package <package_path> <distribution> <component>")
            sys.exit(1)
        package_path = sys.argv[2]
        distribution = sys.argv[3]
        component = sys.argv[4]
        success = manager.add_package(package_path, distribution, component)
        sys.exit(0 if success else 1)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
