# Chemics

## Steps to releasing a new version

- [ ] Run Code Inspection
- [ ] Ensure all code is pushed to master branch
- [ ] Ensure any temporary or testing code is disabled or removed
- [ ] Bump the version *(change **patch** to **minor** or **major** if neccessary)*
  - Dryrun (run from the configs folder in the CLI):  
  `bumpversion patch --config-file .bumpversion.cfg --verbose --allow-dirty --dry-run`
  - Actual (run from the configs folder in the CLI):  
  `bumpversion patch --config-file .bumpversion.cfg`
- [ ] Create windows exe file
   - Windows (run from the configs folder in the CLI):  
   `pyinstaller chemics_win.spec --workpath ../chemics/build --distpath ../chemics/dist --clean`
- [ ] Update Code documentation website
- [ ] Ensure master branch is up to date
- [ ] Push changes to remote
- [ ] Update [Gitlab tag description](https://gitlab.bucknell.edu/nrr004/Chemics/tags) with Changelog comments

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

#### Basic Packages
- [ ] Cython:  0.28.5
- [ ] matplotlib:  2.2.3
- [ ] m2r:  0.2.1
- [ ] numpy:  1.15.1
- [ ] pandas:  0.23.4
- [ ] PySide:  1.2.0
- [ ] scipy:  1.1.0
- [ ] sphinx:  1.8.5
- [ ] sphinx_rtd_theme: 0.4.3

#### Dev Specific [Depends on IDE Choice]:
- [ ] bumpversion: 0.5.3
- [ ] ipykernel:  4.10.0
- [ ] python-language-server:  0.26.1
- [ ] xlwt=1.3.0

#### Windows Specific:
- [ ] pywin32:  223
- [ ] pypiwin32:  223
