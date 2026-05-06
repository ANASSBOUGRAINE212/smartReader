from setuptools import setup, find_packages

setup(
    name='smartreader-pi-server',
    version='1.0.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.9',
    install_requires=[
        'Flask>=3.0.0',
        'Flask-CORS>=4.0.0',
        'Flask-SocketIO>=5.3.5',
        'python-socketio>=5.10.0',
        'opencv-python>=4.8.1',
        'pytesseract>=0.3.10',
        'Pillow>=10.1.0',
        'numpy>=1.26.2',
        'google-cloud-vision>=3.5.0',
        'google-cloud-texttospeech>=2.15.0',
        'googletrans>=4.0.0rc1',
        'TTS>=0.22.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'pytest-cov>=4.1.0',
            'pytest-mock>=3.12.0',
            'hypothesis>=6.92.2',
        ],
    },
)
