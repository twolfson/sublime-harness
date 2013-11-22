from setuptools import setup, find_packages


setup(
    name='sublime_harness',
    version='0.1.1',
    description='Run Python in Sublime Text from outside of Sublime Text',
    long_description=open('README.rst').read(),
    keywords=[
        'sublime text',
        'harness',
        'runner'
    ],
    author='Todd Wolfson',
    author_email='todd@twolfson.com',
    url='https://github.com/twolfson/sublime-harness',
    download_url='https://github.com/twolfson/sublime-harness/archive/master.zip',
    packages=find_packages(),
    license='UNLICENSE',
    install_requires=open('requirements.txt').readlines(),
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Text Editors'
    ]
)
