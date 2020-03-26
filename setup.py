from setuptools import setup, find_packages
import re

setup(
    name='rest-agent',
    version='1.0.2',
    packages=['.'],
    include_package_data=True,
    url='',
    license='',
    author='GodQ',
    author_email='',
    description='',
    install_requires=['flask', 'requests', 'redis'],
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'rest-agent = manage:main',
        ],
    },
)
