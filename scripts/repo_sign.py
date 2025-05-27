#!/usr/bin/env python3
"""
Repository Signing Module

This module handles GPG signing operations for the Debian package repository.
It provides functionality for signing packages, Release files, and managing GPG keys.

The RepoSigner class encapsulates all signing operations and key management tasks.
It ensures the security and authenticity of the repository content through GPG signatures.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from repo_config import RepoConfig

class RepoSigner:
    """
    Repository Signing Class
    
    This class manages GPG signing operations for the repository, including:
    - Signing Release files
    - Signing packages
    - Managing GPG keys
    - Exporting public keys
    
    Attributes:
        logger (Logger): Logging instance for the signer
        gpg_key_id (str): GPG key ID used for signing
    """

    def __init__(self):
        """
        Initialize the repository signer.
        
        Sets up logging and loads GPG key configuration.
        """
        self.logger = self._setup_logging()
        self.gpg_key_id = RepoConfig.GPG_KEY_ID

    def _setup_logging(self):
        """
        Configure logging for the signer.
        
        Returns:
            Logger: Configured logging instance
            
        Sets up logging with appropriate handlers and formatters for both
        file and console output.
        """
        logger = logging.getLogger('RepoSigner')
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(RepoConfig.LOG_FILE)
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(RepoConfig.LOG_FORMAT)
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger

    def sign_release(self, distribution):
        """
        Sign Release file for a distribution.
        
        Args:
            distribution (str): Name of the distribution to sign (e.g., 'stable', 'testing')
            
        Returns:
            bool: True if signing was successful, False otherwise
            
        Creates both a detached signature (.gpg) and a clearsigned version (InRelease)
        of the Release file.
        """
        release_file = RepoConfig.get_dist_path(distribution) / "Release"
        if not release_file.exists():
            self.logger.error(f"Release file not found for {distribution}")
            return False

        try:
            # Create detached signature (Release.gpg)
            cmd = [
                'gpg',
                '--default-key', self.gpg_key_id,
                '-abs',
                '-o', str(release_file.parent / 'Release.gpg'),
                str(release_file)
            ]
            subprocess.run(cmd, check=True)

            # Create inline signature (InRelease)
            cmd = [
                'gpg',
                '--default-key', self.gpg_key_id,
                '--clearsign',
                '-o', str(release_file.parent / 'InRelease'),
                str(release_file)
            ]
            subprocess.run(cmd, check=True)

            self.logger.info(f"Successfully signed Release file for {distribution}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to sign Release file: {e}")
            return False

    def sign_package(self, package_path):
        """
        Sign a Debian package using GPG.
        
        Args:
            package_path (str): Path to the .deb package file
            
        Returns:
            bool: True if signing was successful, False otherwise
            
        Creates a detached ASCII-armored signature for the package.
        """
        try:
            # Create detached signature for the package
            cmd = [
                'gpg',
                '--default-key', self.gpg_key_id,
                '--detach-sign',
                '--armor',
                package_path
            ]
            subprocess.run(cmd, check=True)
            self.logger.info(f"Successfully signed package: {package_path}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to sign package {package_path}: {e}")
            return False

    def export_public_key(self):
        """
        Export the repository's public GPG key.
        
        Returns:
            bool: True if export was successful, False otherwise
            
        Exports the public key in ASCII-armored format to the web directory
        for easy access by repository users.
        """
        try:
            key_file = RepoConfig.WEB_DIR / 'key.gpg'
            cmd = [
                'gpg',
                '--export',
                '--armor',
                self.gpg_key_id
            ]
            with open(key_file, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            self.logger.info(f"Public key exported to {key_file}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to export public key: {e}")
            return False

    def verify_key_availability(self):
        """
        Verify that the configured GPG key is available and valid.
        
        Returns:
            bool: True if key is available and valid, False otherwise
            
        Checks if the configured GPG key exists in the keyring and has
        signing capabilities.
        """
        try:
            cmd = [
                'gpg',
                '--list-secret-keys',
                self.gpg_key_id
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False

def main():
    """
    Main entry point for command-line usage.
    
    Provides command-line interface for signing operations:
    - sign-release: Sign a distribution's Release file
    - sign-package: Sign a package file
    - export-key: Export the public GPG key
    """
    if len(sys.argv) < 2:
        print("Usage: repo_sign.py <command> [args...]")
        print("Commands:")
        print("  sign-release <distribution>")
        print("  sign-package <package_path>")
        print("  export-key")
        sys.exit(1)

    signer = RepoSigner()
    command = sys.argv[1]

    if command == "sign-release":
        if len(sys.argv) != 3:
            print("Usage: repo_sign.py sign-release <distribution>")
            sys.exit(1)
        success = signer.sign_release(sys.argv[2])
        sys.exit(0 if success else 1)

    elif command == "sign-package":
        if len(sys.argv) != 3:
            print("Usage: repo_sign.py sign-package <package_path>")
            sys.exit(1)
        success = signer.sign_package(sys.argv[2])
        sys.exit(0 if success else 1)

    elif command == "export-key":
        success = signer.export_public_key()
        sys.exit(0 if success else 1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
