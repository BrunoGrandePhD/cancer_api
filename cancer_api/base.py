"""
base.py
=======
This submodule defines the SQLAlchemy Declarative Base
(along with tweaks) and other base classes.
"""

import os.path
import gc
import logging
from exceptions import CancerApiException
from utils import open_file
from sqlalchemy import UniqueConstraint, Index, Column, Integer, event
import sqlalchemy.orm.session as BaseSession
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from exceptions import *
from main import app


# ============================================================================================== #
# Base Classes and Metaclasses for cancer_api Objects
# ============================================================================================== #


class DeclarativeMetaMixin(DeclarativeMeta):
    """A metaclass to intercept the creation of classes inheriting
    from the declarative base in order to perform adjustments
    """

    def __init__(cls, classname, bases, dict_):
        # First, ensure that primary keys aren't nullable
        for name, value in dict_.items():
            if type(value) == Column and value.foreign_keys:
                dict_[name].nullable = False
        # Second, ensure that attributes listed in unique_on aren't nullable either
        if "unique_on" in dict_:
            unique_on = dict_["unique_on"]
            for attr in unique_on:
                dict_[attr].nullable = False
        # Then proceed as usual
        super(DeclarativeMetaMixin, cls).__init__(classname, bases, dict_)


class CancerApiObject(object):
    """
    Base object to allow for common class methods
    that apply for table and non-table models.
    """

    @property
    def unique_on(self):
        """List of attributes (as strings) on which each instance should be unique."""
        if not getattr(self, "_unique_on", None):
            raise NotImplementedError("The unique_on` attribute hasn't been implemented "
                                      "for this class (i.e. {}).".format(self.__class__.__name__))
        return self._unique_on

    @unique_on.setter
    def unique_on(self, value):
        if type(value) == str:
            self._unique_on = [value]
        else:
            self._unique_on = value

    def __eq__(self, other):
        # If not the same type, return false right away
        if type(other) is not type(self):
            return False
        # Then compare based on unique_on attributes
        unique_on = self.unique_on
        is_equal = [getattr(self, attr) == getattr(other, attr) for attr in unique_on]
        return all(is_equal)

    def __repr__(self):
        """Improve representation of cancer_api objects
        """
        attrs = []
        if getattr(self, "__mapper__", None):
            attr_list = [col[0] for col in self.__mapper__.columns._data.iteritems()]
        else:
            attr_list = vars(self).keys()
        for attr in attr_list:
            if not attr.startswith("_"):
                attrs.append("{}: {}".format(attr, getattr(self, attr, None).__repr__()))
        return "{}(\n\t{}\n)".format(self.__class__.__name__, ",\n\t".join(attrs))


class BaseMixin(CancerApiObject):
    """Provide methods to Base that are only applicable
    to mapped classes.
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @declared_attr
    def __table_args__(cls):
        addons = []
        if type(cls.unique_on) == list:
            attrs = "_&_".join(cls.unique_on)
            addons.append(UniqueConstraint(*cls.unique_on, name="unique_on_" + attrs))
            addons.append(Index("index_for_" + attrs, *cls.unique_on))
        return tuple(addons)

    @classmethod
    def get_or_create(cls, **kwargs):
        """If a model's unique_on class attribute is defined,
        get_or_create will first search the database for an
        existing instance based on the attributes listed in
        unique_on. Otherwise, it will create an instance.
        Note that the session still needs to be committed.
        """
        # Get session
        session = app.session
        # Create subset of kwargs according to unique_on
        unique_kwargs = {k: v for k, v in kwargs.iteritems() if k in cls.unique_on}
        # Check if instance already exists based on unique_kwargs
        filter_query = session.query(cls).filter_by(**unique_kwargs)
        is_preexisting = session.query(filter_query.exists()).one()[0]
        if is_preexisting:
            # Instance already exists; obtain it and return it
            instance = filter_query.first()
        else:
            # Instance doesn't already exist, so create a new one
            instance = cls(**kwargs)
            session.add(instance)
        return instance

    def add(self):
        """Add self to session"""
        app.session.add(self)
        return self

    def save(self):
        """Add self to session and commit"""
        self.add()
        app.session.commit()
        return self


Base = declarative_base(cls=BaseMixin, metaclass=DeclarativeMetaMixin)


# ============================================================================================== #
# Validators
# ============================================================================================== #

def validate_int(value):
    if isinstance(value, basestring):
        value = int(value)
    else:
        assert isinstance(value, int)
    return value


validators = {
    Integer: validate_int
}


@event.listens_for(Base, 'attribute_instrument')
def configure_listener(class_, key, inst):
    if not hasattr(inst.property, 'columns'):
        return

    @event.listens_for(inst, "set", retval=True)
    def set_(instance, value, oldvalue, initiator):
        validator = validators.get(inst.property.columns[0].type.__class__)
        if validator:
            return validator(value)
        else:
            return value


# ============================================================================================== #
# Sessions
# ============================================================================================== #

class Session(BaseSession.Session):
    """Add convenience methods to Session"""

    def __init__(self, db_cnx, **kwargs):
        self.engine = db_cnx.engine
        super(Session, self).__init__(bind=self.engine, **kwargs)

    def create_tables(self):
        """Creates all tables according to base"""
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Creates all tables according to base"""
        Base.metadata.drop_all(self.engine)


# ============================================================================================== #
# Base Classes for Files and Parsers
# ============================================================================================== #


class BaseFile(object):
    """Base class for file classes"""

    DEFAULT_HEADER = ""
    HEADER_PREFIX = "#"
    FILE_EXTENSIONS = ["txt"]
    COMPRESSION_EXTENSIONS = ["gz", "bz"]

    def __init__(self, *args, **kwargs):
        """Can't initialize directly."""
        raise CancerApiException("Please use `open`, `convert` or `new` methods instead.")

    @classmethod
    def _init(cls, filepath=None, parser_cls=None, other_file=None, is_new=False, buffersize=None):
        """Initialize BaseFile. Any instantiation of BaseFile should
        go through this method in an attempt to standardize attributes.
        Meant to be used internally only.
        """
        obj = cls.__new__(cls)
        obj.filepath = filepath
        obj.parser_cls = parser_cls
        obj.parser = parser_cls(obj) if parser_cls else cls.DEFAULT_PARSER_CLS(obj)
        obj.source = obj if not other_file else other_file.source
        obj.is_new = is_new
        obj.storelist = []
        obj.buffersize = buffersize
        obj._header = None
        return obj

    @classmethod
    def open(cls, filepath, parser_cls=None, buffersize=None):
        """Instantiate a BaseFile object from an
        existing file on disk.
        """
        obj = cls._init(filepath=filepath, parser_cls=parser_cls, other_file=None, is_new=False,
                        buffersize=buffersize)
        return obj

    @classmethod
    def convert(cls, filepath, other_file, buffersize=None):
        """Instantiate a BaseFile object from another
        BaseFile object.
        """
        if not isinstance(other_file, BaseFile):
            raise CancerApiException("Must pass cancer_api file object as `other_file`.")
        obj = cls._init(filepath=filepath, parser_cls=None, other_file=other_file, is_new=True,
                        buffersize=buffersize)
        obj.write()
        return obj

    @classmethod
    def new(cls, filepath, buffersize=None):
        """Instantiate a BaseFile object from scratch.
        Useful for adding objects and write them out to disk.
        """
        obj = cls._init(filepath=filepath, parser_cls=None, other_file=None, is_new=True,
                        buffersize=buffersize)
        return obj

    def get_header(self):
        """Return header if already stored in instance.
        Otherwise, parse file on disk if filepath is specified.
        If not, return default header for current file type.
        """
        if self._header:
            header = self._header
        elif self.is_new:
            # It's a file create with the `new` or `convert` methods
            header = self.DEFAULT_HEADER
        else:
            # It's a file created with the `open` method
            with self._open() as infile:
                header = ""
                for line in infile:
                    if self.is_header_line(line):
                        header += line
                    else:
                        break
        return header

    def set_header(self, new_header):
        """Manually set header of file for next time it is
        written to disk.
        """
        self._header = new_header

    @property
    def col_names(self):
        if getattr(self, "_col_names", None):
            col_names = self._col_names
        else:
            header = self.get_header()
            # Assume that the column names are the
            # last line in the header
            last_header_line = header.rstrip("\n").split("\n")[-1]
            col_names = last_header_line.lstrip(self.HEADER_PREFIX).split("\t")
            self._col_names = col_names
        return col_names

    @col_names.setter
    def col_names(self, value):
        self._col_names = list(value)

    def split_filename(self):
        """Returns filename (root, ext) tuple."""
        filename = os.path.basename(self.filepath)
        # Make sure that long extensions go first (to match the longest available extension)
        for ext in ("." + x.lower() for x in sorted(self.FILE_EXTENSIONS, key=len, reverse=True)):
            if filename.lower().endswith(ext):
                return (filename[:-len(ext)], ext)
            for comp_ext in self.COMPRESSION_EXTENSIONS:
                new_ext = ext + "." + comp_ext
                if filename.lower().endswith(new_ext):
                    return (filename[:-len(new_ext)], new_ext)
        # If none of the class' file extensions match, just use os.path.splitext
        return os.path.splitext(filename)

    @classmethod
    def get_file_extension(cls):
        """Return first extension from cls.FILE_EXTENSIONS.
        Otherwise, returns an error if not available.
        """
        return cls.FILE_EXTENSIONS[0]

    def add_obj(self, obj):
        """Add object to storelist. Useful to bind objects
        to files created with the `new` constructor.
        Returns whether the object was added
        (always True for now).
        """
        if not isinstance(obj, CancerApiObject):
            raise CancerApiException("`add_obj` only supports cancer_api objects")
        self.storelist.append(obj)
        if self.buffersize and len(self.storelist) >= self.buffersize:
            self.write()
        return True

    def clear_storelist(self):
        """Empty storelist"""
        self.storelist = []
        # Force garbage collection
        gc.collect()

    @classmethod
    def is_header_line(cls, line):
        """Return whether or not a line is a header line
        according to the current file type.
        Defaults to lines starting with '#'
        (see BaseFile.HEADER_PREFIX).
        """
        is_header_line = False
        if cls.HEADER_PREFIX and line.startswith(cls.HEADER_PREFIX):
            is_header_line = True
        return is_header_line

    @classmethod
    def obj_to_str(cls, obj):
        """Returns string for representing objects
        as lines (one or many) in current file type.
        If object doesn't have a line representation for
        the current file type, return None.
        """
        # Example implementation:
        # if type(obj) is SingleNucleotideVariant:
        #     line = "{chrom}\t{pos}\t{ref_allele}\t{alt_allele}\n".format(**vars(obj))
        # elif type(obj) is StructuralVariation:
        #     line = "{chrom1}\t{pos1}\t...\n".format(**vars(obj))
        # else:
        #     line = None
        # return line
        raise NotImplementedError

    def _open(self):
        """Use the open_file function on self.source.filepath in 'r' mode"""
        return open_file(self.source.filepath)

    def write(self, outfilepath=None, mode="w"):
        """Write objects in file to disk.
        Either you can write to a new file (if outfilepath is given),
        or you can append what's in storelist to the current filepath.
        """
        # If outfilepath is specified, iterate over every object in self
        # (which might come from something else) and every object in
        # self.storelist and write them out to disk
        if outfilepath:
            with open_file(outfilepath, mode) as outfile:
                logging.info("Writing to disk...")
                outfile.write(self.get_header())
                for obj in self.source:
                    line = self.obj_to_str(obj)
                    outfile.write(line)
                for obj in self.storelist:
                    line = self.obj_to_str(obj)
                    outfile.write(line)
            # Clear storelist now that they've been written to disk
            self.clear_storelist()
            # Update file attributes (in case of new or converted file)
            self.source = self
            self.filepath = outfilepath
            self.is_new = False

        # If outfilepath is not specified, simply iterate over every
        # object in self.storelist and append them to the file on disk.
        else:
            # If the file is new and the path already exist, do not append
            if self.is_new and os.path.exists(self.filepath):
                raise CancerApiException("Output file already exists: {}".format(self.filepath))
            with open_file(self.filepath, "a+") as outfile:
                logging.info("Writing to disk...")
                # If the file is new, start with header
                if self.is_new:
                    outfile.write(self.get_header())
                # If file is new and source is not self (i.e., converted file),
                # iterate over source
                if self.is_new and self.source is not self:
                    for obj in self.source:
                        line = self.obj_to_str(obj)
                        outfile.write(line)
                # Proceed with iterating over storelist
                for obj in self.storelist:
                    line = self.obj_to_str(obj)
                    outfile.write(line)
            # Clear storelist now that they've been written to disk
            self.clear_storelist()
            # Update file attributes (in case of new or converted file)
            self.source = self
            self.is_new = False

    def close(self):
        """Ensure that buffer is written out to disk
        """
        if len(self.storelist) > 0:
            self.write()

    def iterlines(self, include_obj=False):
        """Iterate over non-comment lines.
        Provides option to parse line and return
        object alongside line as tuple.
        """
        with self._open() as infile:
            for line in infile:
                if self.source.is_header_line(line):
                    continue
                if include_obj:
                    obj = self.source.parser.parse(line)
                    if obj:
                        yield (line, obj)
                else:
                    yield line

    def __iter__(self):
        """Return instances of the objects
        associated with the current file type.
        """
        for line, obj in self.iterlines(include_obj=True):
            yield obj


class BaseParser(object):
    """Base file parser for defining necessary methods."""

    def __init__(self, file):
        """Store related file internally."""
        self.file = file

    def basic_parse(self, line):
        """The basic_parse method serves to create
        a dictionary of (column name, value) pairs.
        This is to provide a common base for all
        derivative parsers.

        Returns a dict of (column name, value) pairs.
        """
        raise NotImplementedError

    def parse(self, line):
        """The parse method is user-facing and serves
        to return object instances as opposed to the
        dictionaries returned by _parse.

        Returns a cancer_api object instance
        """
        raise NotImplementedError
