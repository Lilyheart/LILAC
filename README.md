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

## Steps for testing dead code

This uses the [vulture package](https://github.com/jendrikseipp/vulture).

- [ ] From the CLI while in the top level folder, execture `vulture chemics/ configs/vulture_whitelist.py`
    
## Programming Environment
    
### Using requirements.txt
    
#### Conda
    
##### Linux
    
```bash
conda create --name Chemics37 --file requirements-linux64.txt
```
    
<!--
##### Windows

 TODO -->
    
### Manually installing packages

If using Anaconda, ensure the `conda-forge` channel has been added.

Python version: **3.6.8**

#### Basic Packages required to run Chemics
- [ ] Cython:  0.29.12
- [ ] matplotlib:  3.1.1
- [ ] numpy:  1.16.4
- [ ] pandas:  0.24.2
- [ ] PySide:  1.2.4 
- [ ] scipy:  1.3.0

#### Dev Specific [May also depend on IDE Choice]:
##### Code Developement
- [ ] ipykernel:  5.1.1
- [ ] jupyter:  1.0.0
- [ ] python-language-server:  0.28.0
- [ ] vulture:  1.0
- [ ] xlwt:  1.3.0
##### Code Documentation
- [ ] m2r:  0.2.1
- [ ] pycallgraph:  1.0.1 ***(pip install pycallgraph)***
- [ ] sphinx:  2.1.2
- [ ] sphinx_rtd_theme:  0.4.3
##### Executable Creation
- [ ] bumpversion:  0.5.3
- [ ] pyinstaller:  3.4

