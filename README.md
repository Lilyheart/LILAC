# Chemics

## Programming Environment

### Using requirements.txt

#### Conda

##### Linux

```bash
conda create -y -n Chemics27 python==2.7.16
conda install -n Chemics27 --override-channels -c conda-forge anaconda --file requirements-linux64.txt
```

<!--
##### Windows

 TODO -->

### Manually installing packages

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

### Dev Specific [Depends on IDE Choice]:
- [ ] ipykernel:  4.10.0
- [ ] python-language-server:  0.26.1
- [ ] xlwt=1.3.0

### Windows Specific:
- [ ] pywin32:  223
- [ ] pypiwin32:  223
