from setuptools import setup, find_packages

setup(
    name='video_renamer',
    version='1.0',
    packages=find_packages(),
    install_requires=['ffmpeg-python'],
    entry_points={
        'console_scripts': [
            'video_renamer=video_renamer.main:main',  # module chemin vers la fonction main
        ],
    },
)
