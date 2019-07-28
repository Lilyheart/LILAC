# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
### Added for new features.
### Fixed for any bug fixes.
### Changed for changes in existing functionality.
### Deprecated for soon-to-be removed features.
### Removed for now removed features.
### Security in case of vulnerabilities.
([#](https://gitlab.bucknell.edu/nrr004/Chemics/issues/))
-->


## [Unreleased]
### Changed
- Updated entire code base to Python 3.6.8


## [2.2.3] - 2019-07-26
### Fixed
- Ratio vs DD graph showing old data from previous valid scan

### Changed
- Autoshift peak recognition


## [2.2.2] - 2019-07-19
### Added
- Sigmoid fit on single scan
- Sigmoid status on sigmoid parameters screen
- Scan index to Kappa Table
- Scan index to Kappa CSV
- Window shows parent folder of raw data location

### Fixed
- Exported Kappa CSV files to now be named after the parent folder like the project run file is.
- Various window titles

### Changed
- Percent Activation to show "Unknown" when unable to calculate


## [2.2.1] - 2019-07-18
### Added 
- Background color on sigmoid graph when scan is invalid
- Percent Activation ([#32](https://gitlab.bucknell.edu/nrr004/Chemics/issues/32))

### Fixed 
- Graph titles and tweaks
- Sigmoid parameter rounding and step values
- Super saturation updated to supersaturation ([#55](https://gitlab.bucknell.edu/nrr004/Chemics/issues/55))

### Removed
- Backwards compability of project run files


## [2.2.0] - 2019-07-17
### Added
- Instructions on README on how to use the vulture package to find unused code
- Ability to override Supersaturation ([#13](https://gitlab.bucknell.edu/nrr004/Chemics/issues/13))
- Error Logging

### Fixed
- Kappa Parameters issue ([#65](https://gitlab.bucknell.edu/nrr004/Chemics/issues/65))

### Changed
- Sigmoid Fit Algorithm ([#42](https://gitlab.bucknell.edu/nrr004/Chemics/issues/42))
- Various graph tweaks  ([#54](https://gitlab.bucknell.edu/nrr004/Chemics/issues/54)) ([#26 Partial](https://gitlab.bucknell.edu/nrr004/Chemics/issues/26))
- File names are sorted alphabetically to ensure files are parsed in correct order ([#44](https://gitlab.bucknell.edu/nrr004/Chemics/issues/44))


## [2.1.2] - 2019-07-10
### Added 
- Instructions in README on how to update version numbers and build on windows.

### Changed
- Updated end asymp for sigmoid to the minimum of 100 or the largest average SMPS diameter ([#62](https://gitlab.bucknell.edu/nrr004/Chemics/issues/62))


## [2.1.1] - 2019-07-09
### Added
- The name of the folder is stored when opening a new or old project ([#11](https://gitlab.bucknell.edu/nrr004/Chemics/issues/11))
  - For a new project, the parent of the folder of the 
    source files is saved.
  - For an old project, the folder the .chemics file was located
    in is saved.
- When saving a project or exporting Kappa data, the folder stored from above is presented as the default folder. ([#11](https://gitlab.bucknell.edu/nrr004/Chemics/issues/11))
- requirements-linux64.txt for dev environment installs
- Supersaturation to Sigmoid Parameters screen ([#1](https://gitlab.bucknell.edu/nrr004/Chemics/issues/1))
- Scan identifying information to sigmoid parameters screen ([#17](https://gitlab.bucknell.edu/nrr004/Chemics/issues/17))
- When choosing to exit, either from the file menu or the main window's exit button, prompt the user if they want to exit or save **if** a run has been started. ([#53](https://gitlab.bucknell.edu/nrr004/Chemics/issues/53))
- Added hover details on Kappa chart ([#19 partial](https://gitlab.bucknell.edu/nrr004/Chemics/issues/19))
  - Hovering over a line tell you which kappa line
  - Hovering over a point tells you the DP50 and supersaturation

### Fixed
- Bug where end asymp truncates to 99.99 ([#29](https://gitlab.bucknell.edu/nrr004/Chemics/issues/29))
- Bug where supersaturation did not display correctly on the Scan Information screen ([#2](https://gitlab.bucknell.edu/nrr004/Chemics/issues/2))
  - If more than one, will display both.  E.g. `0.2, 0.5`

### Changed
- Hid all side widgets with the exception of the Scan Information 
  widget on load.
- Changes to Help menu ([#23 Partial](https://gitlab.bucknell.edu/nrr004/Chemics/issues/23))
  - New link to temporary user manual
  - New link to About window to display current version

### Removed
- Removed run reset code ([#53](https://gitlab.bucknell.edu/nrr004/Chemics/issues/53))


## [2.1.0] - 2019-06-21
### Added
- Packaged in onefile ([#9](https://gitlab.bucknell.edu/nrr004/Chemics/issues/9))
                            - Export Kappa now askes you where you want to save the csv file. ([#11 partial](https://gitlab.bucknell.edu/nrr004/Chemics/issues/11))

### Fixed
- Date, Scan duration, number of scans, const2concconv, scan time, super saturation and scan status no longer show default values when application is first opened ([#5](https://gitlab.bucknell.edu/nrr004/Chemics/issues/5))
- Date, Scan duration, number of scans, const2concconv, scan time, and scan status update correctly when cycling through scans ([#5](https://gitlab.bucknell.edu/nrr004/Chemics/issues/5))

### Changed
- Scan information section tweaked for button flow
- Settings moved to help menu.

### Removed
- Uncoded help menu items disabled ([#23 partial](https://gitlab.bucknell.edu/nrr004/Chemics/issues/23))
- Select smoothing algorithm removed from opening new project. ([#41](https://gitlab.bucknell.edu/nrr004/Chemics/issues/41))
- Smooth Data removed from Action dropdown menu ([#41](https://gitlab.bucknell.edu/nrr004/Chemics/issues/41))
