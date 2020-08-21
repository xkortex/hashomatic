from setuptools import find_packages, setup
import versioneer

commands = versioneer.get_cmdclass().copy()

pkgname = 'hashomatic'

packages = find_packages()
print('Packages:', packages)

# common dependencies
deps = [
    "boltons",
]

deps_test = ['xdoctest']
deps_sci = ['numpy', 'pandas', 'sklearn']

setup(
    name=pkgname,
    version=versioneer.get_version(),
    script_name='setup.py',
    python_requires='>3.6',
    zip_safe=False,
    packages=packages,
    install_requires=deps,
    extras_require={
        'test': ['xdoctest'],
        'sci': deps_sci,
        'all': deps_test + deps_sci
    },
    cmdclass=commands,
)
