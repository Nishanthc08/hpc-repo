# debian-hpc Repository

A Debian-style package repository system designed for High Performance Computing packages.

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/debian-hpc.git
cd debian-hpc
```

2. Install dependencies:
```bash
sudo apt-get install python3 python3-flask dpkg-dev gnupg2 apache2 devscripts build-essential debhelper
```

3. Initialize the repository:
```bash
./manage.py init
```

4. Add a test package:
```bash
cd scripts
./create_test_package.py hpc-test 1.0.0 "Test package for HPC repository"
cd ..
./manage.py add-package scripts/hpc-test_1.0.0_all.deb stable main
```

5. Start the web interface:
```bash
cd web
python3 app.py
```

Access the repository at http://localhost:8080

## Documentation

See [DOCUMENTATION.md](DOCUMENTATION.md) for complete documentation, including:
- Detailed setup instructions
- Repository management
- Package creation
- Security configuration
- Web interface details
- Troubleshooting guide

## Security

All packages and repository metadata are signed with GPG. The repository uses strong security practices including:
- GPG signing of all packages
- Signed Release files
- Secure web interface
- Proper permission management

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please create an issue in the GitHub repository.
