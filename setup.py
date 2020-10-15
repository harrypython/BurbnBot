import setuptools

project_homepage = "https://github.com/harrypython/BurbnBot"

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    dependencies = f.read().splitlines()

setuptools.setup(
    name='BurbnBot',
    version='1.0',
    packages=setuptools.find_packages(),
    url='https://github.com/harrypython/BurbnBot',
    license='GPL-3.0',
    author='Harry Python',
    author_email='harrypython@protonmail.com',
    description='BurbnBot is a bot for automated interaction in a famous social media app using a Android device '
                'or an Android Virtual Devices.',
    project_urls={
        "Example": (project_homepage + "/blob/master/example.py"),
        "Bug Reports": (project_homepage + "/issues"),
        "Buy me a coffee": "https://www.buymeacoffee.com/harrypython",
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
    install_requires=dependencies,
)
