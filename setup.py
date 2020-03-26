from setuptools import setup, find_packages

setup(
    name='rest-agent',
    version='1.0.1',
    packages=['.'],
    include_package_data=True,
    url='',
    license='',
    author='GodQ',
    author_email='',
    description='',
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
