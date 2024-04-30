from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="blackjack-calculator-closed-form",
        packages=find_packages(),
        install_requires=[
            "numpy",
            "pandas",
        ],
    )
