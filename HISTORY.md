Release History
===============


Next version
------------------

**Features and Enhancements**

- Implemented method to check for overlap with genomic region for SVs

**Bugfixes**

- None


0.2.1 (2015-03-28)
------------------

**Bugfixes**

- Fixed (and renamed) method for getting file extension in BaseFile
- Generalized support for compression file extensions


0.2.0 (2015-03-24)
------------------

**Features and Enhancements**

- Added Factera file type and parser
- Added PavFinder VCF file type and parser
- Refactored BaseFile to be more consistent and stable
	- Common instantiation method to ensure consistent attributes
	- add_obj now checks if obj is a CancerApiObject
	- Added buffersize option for files for autoflushing
	- Converted files automatically write out to disk

**Bugfixes**

- Fixed bugs relating to file conversion


0.1.5 (2015-03-09)
------------------

**Bugfixes**

- Fixed uninitialized attributes in BaseFile


0.1.4 (2015-03-04)
------------------

**Features and Enhancements**

- Moved garbage collection (for reduced memory usage) to `clear_storelist` method

**Bugfixes**

- The files submodule would incorrectly append to the same file between different runs. This has been fixed.


0.1.3 (2015-03-03)
------------------

First version to be uploaded to PyPI (version bumped for naming reasons). 


0.1.2 (2015-03-03)
------------------

**Features and Improvements**

- Force garbage collection after writing out objects to disk.
- Remove check for duplicates when adding objects to file storelist (for performance)


0.1.1 (2015-03-03)
------------------

**Features and Improvements**

- Improved implementation of `Chronometer` utils class.

**Bugfixes**

- `Chronometer.lap` method now prints difference in time since last lap instead of accumulated time.


0.1.0 (2015-01-22)
------------------

Initial version. 
