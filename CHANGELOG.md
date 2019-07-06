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
### Added
- The name of the folder is stored when opening a new or old project ([#11](https://gitlab.bucknell.edu/nrr004/Chemics/issues/11))
  - For a new project, the parent of the folder of the 
    source files is saved.
  - For an old project, the folder the .chemics file was located
    in is saved.
- When saving a project or exporting Kappa data, the folder stored from above is presented as the default folder.([#11](https://gitlab.bucknell.edu/nrr004/Chemics/issues/11))
- requirements-linux64.txt for dev environment installs
- Supersaturation to Sigmoid Parameters screen ([#1](https://gitlab.bucknell.edu/nrr004/Chemics/issues/1))
- Scan identifying information to sigmoid parameters screen ([#17](https://gitlab.bucknell.edu/nrr004/Chemics/issues/17))
- When chosing to exit, either from the file menu or the main window's exit button, prompt the user if they want to exit or save **if** a run has been started. ([#53](https://gitlab.bucknell.edu/nrr004/Chemics/issues/53))

### Fixed
- Bug where end asymp truncates to 99.99 ([#29](https://gitlab.bucknell.edu/nrr004/Chemics/issues/29))
- Bug where supersaturation did not display correctly on the Scan Information screen ([#2](https://gitlab.bucknell.edu/nrr004/Chemics/issues/2))

### Changed
- Hid all side widgets with the exception of the Scan Information 
  widget on load.
  
### Removed
- Removed run reset code ([#53](https://gitlab.bucknell.edu/nrr004/Chemics/issues/53))

## [2.1.0] - 2019-06-21
### Added
- Packaged in onefile ([#9](https://gitlab.bucknell.edu/nrr004/Chemics/issues/9))
- Export Kappa now askes you where you want to save the csv file. ([#11 partial](https://gitlab.bucknell.edu/nrr004/Chemics/issues/11))

### Fixed
- Date, Scan duration, number of scans, const2concconv, scan time, super saturation and scan status no longer show default values when application is first opened ([#5](https://gitlab.bucknell.edu/nrr004/Chemics/issues/5))
- Date, Scan duration, number of scans, const2concconv, scan time, super saturation and scan status update correctly when cycling through scans ([#5](https://gitlab.bucknell.edu/nrr004/Chemics/issues/5))

### Changed
- Scan information section tweaked for button flow
- Settings moved to help menu.

### Removed
- Uncoded help menu items disabled ([#23 partial](https://gitlab.bucknell.edu/nrr004/Chemics/issues/23))
- Select smoothing algorithm removed from opening new project. ([#41](https://gitlab.bucknell.edu/nrr004/Chemics/issues/41))
- Smooth Data removed from Action dropdown menu ([#41](https://gitlab.bucknell.edu/nrr004/Chemics/issues/41))

