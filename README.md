# Chemics

## Programming Environment

If using Anaconda, ensure the `conda-forge` channel has been added.

Python version: **2.7.16**

### Basic Packages
- [ ] Cython:  0.28.5
- [ ] matplotlib:  2.2.3
- [ ] m2r:  0.2.1
- [ ] numpy:  1.15.1
- [ ] pandas:  0.23.4
- [ ] PySide:  1.2.0
- [ ] scipy:  1.1.0
- [ ] sphinx:  1.8.5
- [ ] sphinx_rtd_theme: 0.4.3

All in one command line for the above:
```
conda create -n chemics python=2.7.16 Cython=0.28.5 matplotlib=2.2.3 m2r=0.2.1 pandas=0.23.4 PySide=1.2.0 scipy=1.1.0 sphinx=1.8.5 sphinx_rtd_theme=0.4.3
```

### Dev Specific [Depends on IDE Choice]:
- [ ] ipykernel:  4.10.0
- [ ] python-language-server:  0.26.1
- [ ] xlwt=1.3.0

Update Versions all in one command line for the above:
```
conda create -n chemics python=2.7.16 Cython=0.28.5 matplotlib=2.2.3 m2r=0.2.1 pandas=0.23.4 PySide=1.2.0 scipy=1.1.0 sphinx=1.8.5 sphinx_rtd_theme=0.4.3 ipykernel=4.10.0 python-language-server=0.26.1 xlwt=1.3.0
```

### Windows Specific:
- [ ] pywin32:  223
- [ ] pypiwin32:  223
