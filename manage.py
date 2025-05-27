#!/usr/bin/env python3
"""
Repository Management Script

This is the main management script for the Debian-style package repository.
It provides a unified interface for all repository management operations,
integrating package management, signing, and repository maintenance tasks.

The script serves as the primary entry point for repository administration,
coordinating between different components of the system.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add scripts directory to Python path
sys.path.append(str(Path(__file__).parent / 'scripts'))

from repo_config import RepoConfig
from repo_manager import DebianRepoManager
from repo_sign import RepoSigner

def setup_logging():
    """
    Configure logging for the management script.
    
    Sets up logging with appropriate handlers and formatters for both
    file and console output.
    
    Returns:
        Logger: Configured logging instance
    """
    logging.basicConfig(
        level=getattr(logging, RepoConfig.LOG_LEVEL),
        format=RepoConfig.LOG_FORMAT,
        handlers=[
            logging.FileHandler(RepoConfig.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('manage')

class RepositoryManager:
    """
    Main Repository Management Class
    
    This class coordinates all repository management operations by integrating
    package management, signing, and maintenance functionality.
    
    Attributes:
        logger (Logger): Logging instance
        repo_manager (DebianRepoManager): Package management instance
        signer (RepoSigner): GPG signing instance
    """

    def __init__(self):
        """Initialize the repository manager with all required components."""
        self.logger = setup_logging()
        self.repo_manager = DebianRepoManager(RepoConfig.BASE_DIR)
        self.signer = RepoSigner()

    def add_package(self, package_path, distribution, component):
        """
        Add a package to the repository.
        
        This method coordinates the complete package addition process:
        1. Validates the package
        2. Adds it to the repository
        3. Signs the package
        4. Updates and signs repository metadata
        
        Args:
            package_path (str): Path to the .deb package file
            distribution (str): Target distribution (e.g., 'stable', 'testing')
            component (str): Target component (e.g., 'main', 'contrib')
            
        Returns:
            bool: True if all operations were successful, False otherwise
        """
        if not os.path.exists(package_path):
            self.logger.error(f"Package file not found: {package_path}")
            return False

        if distribution not in RepoConfig.DISTRIBUTIONS:
            self.logger.error(f"Invalid distribution: {distribution}")
            return False

        if component not in RepoConfig.COMPONENTS:
            self.logger.error(f"Invalid component: {component}")
            return False

        # Add package to repository
        if not self.repo_manager.add_package(package_path, distribution, component):
            return False

        # Sign the package
        if not self.signer.sign_package(package_path):
            return False

        # Update and sign the Release file
        if not self.signer.sign_release(distribution):
            return False

        return True

    def update_indices(self, distribution=None):
        """
        Update repository indices.
        
        Updates package indices and signs Release files for specified
        distribution or all distributions.
        
        Args:
            distribution (str, optional): Specific distribution to update.
                If None, updates all distributions.
        """
        distributions = [distribution] if distribution else RepoConfig.DISTRIBUTIONS
        
        for dist in distributions:
            self.logger.info(f"Updating indices for {dist}")
            self.repo_manager.update_indices(dist, None)  # Update all components
            self.signer.sign_release(dist)

    def init_repository(self):
        """
        Initialize or reinitialize the repository structure.
        
        Creates all necessary directories and files for a new repository
        or reinitializes an existing one.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self.logger.info("Initializing repository structure...")
        
        try:
            # Create base directories
            for directory in [RepoConfig.POOL_DIR, RepoConfig.DISTS_DIR, 
                            RepoConfig.WEB_DIR, RepoConfig.LOG_DIR]:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created directory: {directory}")

            # Export GPG key
            self.signer.export_public_key()

            # Initialize distribution structure
            for dist in RepoConfig.DISTRIBUTIONS:
                dist_path = RepoConfig.get_dist_path(dist)
                for component in RepoConfig.COMPONENTS:
                    for arch in RepoConfig.ARCHITECTURES:
                        (dist_path / component / f"binary-{arch}").mkdir(parents=True, exist_ok=True)
                    (dist_path / component / "source").mkdir(parents=True, exist_ok=True)

            self.logger.info("Repository initialization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Repository initialization failed: {e}")
            return False

def main():
    """
    Main entry point for the management script.
    
    Provides command-line interface for repository management:
    - init: Initialize repository structure
    - add-package: Add a new package
    - update: Update repository indices
    """
    parser = argparse.ArgumentParser(description='Debian HPC Repository Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize repository structure')

    # Add package command
    add_parser = subparsers.add_parser('add-package', help='Add a package to the repository')
    add_parser.add_argument('package_path', help='Path to the package file')
    add_parser.add_argument('distribution', help='Target distribution')
    add_parser.add_argument('component', help='Target component')

    # Update indices command
    update_parser = subparsers.add_parser('update', help='Update repository indices')
    update_parser.add_argument('--distribution', help='Specific distribution to update')

    args = parser.parse_args()
    manager = RepositoryManager()

    if args.command == 'init':
        success = manager.init_repository()
    elif args.command == 'add-package':
        success = manager.add_package(args.package_path, args.distribution, args.component)
    elif args.command == 'update':
        success = manager.update_indices(args.distribution)
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
