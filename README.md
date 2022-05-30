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

- [ ] Create Programming Environment
- [ ] Create fast_dp file specific to your os.  Run from the chemics package folder `python fast_dp_setup.py build_ext --inplace`

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

#### Dev Specific [May also depend on IDE Choice]

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

## Creating an environment for LILAC on MacOS on Ubuntu using Conda

- [ ] tl;dr
  - `conda create --name Lilac36 bumpversion=0.5.3 cython=0.29.12 ipykernel=5.1.1
      jupyter=1.0.0 m2r=0.2.1 matplotlib=3.1.1 mkl=2019.4 numpy=1.16.4 pandas=0.24.2
      pyinstaller=3.4 PySide2=5.9.0a1 python=3.6.8 python-language-server=0.28.0
      scipy=1.3.0 sphinx=2.1.2 sphinx_rtd_theme=0.4.3 vulture=1.0 xlwt=1.3.0 -c conda-forge`
  - `conda activate Lilac36`
  - `pip install pycallgraph`
  - From the `\chemics` folder from within the repo run `python fast_dp_setup.py build_ext --inplace`
  - From the `\chemics` folder from within the repo run `python main.py`

## Creating an environment for LILAC on Windows using Conda

- [ ] Install Miniconda
  - Downloaded install exec: `https://repo.anaconda.com/miniconda/Miniconda3-py39_4.9.2-Windows-x86_64.exe`
  - Ran install exec:
    - [Can determine the options I used if you need it]
  - Install `Build Tools for Visual Studio` (Tools for Visual Studio -> Build Tools)
      `https://visualstudio.microsoft.com/downloads/`
    - Select Desktop development with C++
  - Restarted the "computer"
- [ ] Install git and pip - make ssh key for gitlab
  - `conda install -c anaconda git`
  - `conda install -c anaconda pip`
  - `ssh-keygen` and all that
- [ ] Using `-c` inline Channel command
  - Commands are entered using the Anaconda Prompt (miniconda3) [Not the powershell version]
  - Create the environment
  - `conda create --name Lilac36 bumpversion=0.5.3 cython=0.29.12 ipykernel=5.1.1
      jupyter=1.0.0 m2r=0.2.1 matplotlib=3.1.1 mkl=2019.4 numpy=1.16.4 pandas=0.24.2
      pyinstaller=3.4 PySide2=5.9.0a1 python=3.6.8 python-language-server=0.28.0
      scipy=1.3.0 sphinx=2.1.2 sphinx_rtd_theme=0.4.3 vulture=1.0 xlwt=1.3.0 -c conda-forge`
  - Activate
    - `conda activate Lilac36`
  - Install pycallgraph
    - `pip install pycallgraph`
  - Clone
    - `git clone git@gitlab.bucknell.edu:lilac/LILAC.git`
    - `cd LILAC`
  - Build the cython file
    - From the `\chemics` folder from within the repo run python `fast_dp_setup.py build_ext --inplace`
  - Run chemics
    - From the `\chemics` folder from within the repo run `python main.py`

## Install redo 6/11 due to weird pyinstaller things

## Using `c` inline Channel command

- [ ] Install new environment - same as before but with new packages
- [ ] Adding all the following makes it work:
  - m2w64-gcc-libs=5.3.0
  - msys2-conda-epoch=20160418
  - numpy-base=1.16.4
  - asn1crypto=0.24.0
  - smmap2=2.0.5
  - mkl_fft=1.0.12 (6)
  - mkl_random=1.0.2 (7)
  - gitdb2=2.0.5
  - gitpython=3.0.2
  - python-gitlab=1.12.1
- [ ] `conda create --name Lilac36Test9 bumpversion=0.5.3 cython=0.29.12 ipykernel=5.1.1
  jupyter=1.0.0 m2r=0.2.1 matplotlib=3.1.1 mkl=2019.4 numpy=1.16.4 pandas=0.24.2
  pyinstaller=3.4 PySide2=5.9.0a1 python=3.6.8 python-language-server=0.28.0 scipy=1.3.0
  sphinx=2.1.2 sphinx_rtd_theme=0.4.3 vulture=1.0 xlwt=1.3.0 -c conda-forge`

- [ ] Activate
  - `conda activate Lilac36Test9`
  
- [ ] Install pycallgraph
  - `pip install pycallgraph`
  
- [ ] Assuming already cloned and cython file has already been built

- [ ] Run chemics
  - `cd LILAC\chemics`
  - From the `\chemics` folder from within the repo run `python main.py`

- [ ] Build EXE
  - `cd ..\configs`
  - `pyinstaller chemics_win.spec --workpath ../chemics/build --distpath ../chemics/dist --clean`

## Problems?

### Problems building fast_dp_calculator

#### cl.exe missing [Windows]

- [ ] Install [Build Tools for Visual Studio](https://visualstudio.microsoft.com/downloads/) (Tools for Visual Studio -> Build Tools)
- [ ] Restart the computer.  This should add cl.exe into your `PATH`, otherwise you may need to manually add it.
