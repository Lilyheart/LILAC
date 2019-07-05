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
-->

## [Unreleased]
### Added
- The name of the folder is stored when opening a new or old project
  - For a new project, the parent of the folder of the 
    source files is saved.
  - For an old project, the folder the .chemics file was located
    in is saved.
- When saving a project or exporting Kappa data, the folder stored from above is presented as the default folder.
- requirements-linux64.txt for dev environment installs

### Fixed
- Bug where end asymp truncates to 99.99

### Changed
- Hid all side widgets with the exception of the Scan Information 
  widget on load.

## [2.1.0] - 2019-06-21
### Added
- Packaged in onefile
- Export Kappa now askes you where you want to save the csv file.

### Fixed
- Date, Scan duration, number of scans, const2concconv, scan time, super saturation and scan status no longer show default values when application is first opened

### Changed
- Scan information section tweaked for button flow
- Settings moved to help menu.

### Removed
- Uncoded help menu items disabled
- Select smoothing algorithm removed from opening new project.
- Smooth Data removed from Action dropdown menu

