from pathlib import Path
from typing import List

from setuptools import find_packages, setup

BASE = Path(__file__).parent
REQUIREMENTS_DIR = BASE / 'requirements'


def get_requirements(filename: str) -> List[str]:
    with open(REQUIREMENTS_DIR / filename) as file:
        return [ln.strip() for ln in file.readlines()]


essential_packages = get_requirements('essential.txt')
api_service_packages = get_requirements('docker/api.txt')
dashboard_service_packages = get_requirements('docker/dashboard.txt')
worker_service_packages = get_requirements('docker/worker.txt')
dev_packages = get_requirements('dev.txt')


setup(
    name='aifriend',
    version='0.1',
    license='Apache License 2.0',
    author='Alexander Shulga',
    author_email='alexandershulga.sh@gmail.com',
    description='AI fried based on Falcon-7B LLM.',
    python_requires='>=3.8',
    packages=find_packages(
        where='src'
    ),
    package_dir={'': 'src'},
    install_requires=[essential_packages],
    extras_require={
        'api': api_service_packages,
        'dashboard': dashboard_service_packages,
        'worker': worker_service_packages,
        'dev': dev_packages,
    },
    entry_points={
        'console_scripts': [
            'aifriend = aifriend.app.cli.aifriendcli:cli',
        ],
    },
)
