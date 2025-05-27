#!/usr/bin/env python3
"""
Repository Configuration Module

This module defines the core configuration settings for the Debian-style package repository.
It includes paths, repository structure, GPG settings, and other essential parameters.

The RepoConfig class serves as a central configuration point for the entire repository system,
providing consistent settings across all components.
"""

import os
from pathlib import Path

class RepoConfig:
    """
    Repository Configuration Class
    
    This class contains all configuration parameters for the repository system.
    It uses class attributes to provide a singleton-like configuration access.
    
    Attributes:
        REPO_NAME (str): The name of the repository
        REPO_DESCRIPTION (str): A brief description of the repository
        REPO_VERSION (str): The version of the repository software
        DISTRIBUTIONS (list): Available distribution branches (e.g., stable, testing)
        COMPONENTS (list): Available repository components (main, contrib, non-free)
        ARCHITECTURES (list): Supported CPU architectures
        GPG_KEY_ID (str): The GPG key ID used for signing packages and metadata
        Various path configurations for repository structure
    """
    
    # Repository Information
    REPO_NAME = "debian-hpc"
    REPO_DESCRIPTION = "High Performance Computing Debian Repository"
    REPO_VERSION = "1.0.0"

    # Repository Structure
    # These lists define the basic organization of the repository
    DISTRIBUTIONS = ["stable", "testing"]  # Available distribution branches
    COMPONENTS = ["main", "contrib", "non-free"]  # Package components
    ARCHITECTURES = ["amd64", "i386"]  # Supported architectures

    # GPG Configuration
    # Used for signing packages and repository metadata
    GPG_KEY_ID = "D8D87602D00F0680F44BD468F90FBC2AE63EB38F"
    GPG_SIGNING_USER = "Nishanth <nishanthc264@gmail.com>"

    # Web Interface Configuration
    # Settings for the Flask web application
    WEB_HOST = "localhost"  # Web interface host
    WEB_PORT = 8080        # Web interface port
    WEB_TITLE = "debian-hpc Repository"

    # Path Configuration
    # All paths are relative to the repository root directory
    BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    POOL_DIR = BASE_DIR / "pool"      # Package storage
    DISTS_DIR = BASE_DIR / "dists"    # Distribution metadata
    WEB_DIR = BASE_DIR / "web"        # Web interface files
    LOG_DIR = BASE_DIR / "logs"       # Log files

    # Create required directories if they don't exist
    LOG_DIR.mkdir(exist_ok=True)

    # Logging Configuration
    LOG_FILE = LOG_DIR / "repo.log"
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Package validation settings
    # Required fields in package control files
    REQUIRED_FIELDS = [
        "Package",
        "Version",
        "Architecture",
        "Maintainer",
        "Description"
    ]

    @classmethod
    def get_dist_path(cls, distribution):
        """
        Get the filesystem path for a specific distribution.
        
        Args:
            distribution (str): Name of the distribution (e.g., 'stable', 'testing')
            
        Returns:
            Path: Path object pointing to the distribution directory
        """
        return cls.DISTS_DIR / distribution

    @classmethod
    def get_pool_path(cls, component):
        """
        Get the filesystem path for a specific component in the pool.
        
        Args:
            component (str): Name of the component (e.g., 'main', 'contrib')
            
        Returns:
            Path: Path object pointing to the component directory in the pool
        """
        return cls.POOL_DIR / component

    @classmethod
    def get_release_file(cls, distribution):
        """
        Get the path to a distribution's Release file.
        
        Args:
            distribution (str): Name of the distribution
            
        Returns:
            Path: Path object pointing to the Release file
        """
        return cls.get_dist_path(distribution) / "Release"

    @classmethod
    def validate_structure(cls):
        """
        Validate the repository directory structure.
        
        Returns:
            bool: True if the structure is valid, False otherwise
        """
        try:
            # Check main directories
            for dir_path in [cls.POOL_DIR, cls.DISTS_DIR, cls.WEB_DIR, cls.LOG_DIR]:
                if not dir_path.exists():
                    return False

            # Check pool components
            for component in cls.COMPONENTS:
                if not (cls.POOL_DIR / component).exists():
                    return False

            # Check distribution structure
            for dist in cls.DISTRIBUTIONS:
                dist_path = cls.get_dist_path(dist)
                if not dist_path.exists():
                    return False
                
                # Check component directories
                for comp in cls.COMPONENTS:
                    comp_path = dist_path / comp
                    if not comp_path.exists():
                        return False
                    
                    # Check architecture directories
                    for arch in cls.ARCHITECTURES:
                        if not (comp_path / f"binary-{arch}").exists():
                            return False
                    
                    # Check source directory
                    if not (comp_path / "source").exists():
                        return False

            return True
        except Exception:
            return False
