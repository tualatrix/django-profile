from setuptools import setup, find_packages

setup(name='userprofile',
        version='0.6',
        description='Django pluggable user profile zone',
        author='David Rubert',
        packages=find_packages(),
        classifiers=['Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Utilities'],
    include_package_data=True,
    install_requires=['setuptools'],
)
