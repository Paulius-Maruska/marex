#!/usr/bin/python
# -*- coding: utf-8 -*-
from google.appengine.api import files
from google.appengine.ext import blobstore

def remove_files(*args, **kwargs):
    """
    Attempts to delete all blobs identified by passed in positional arguments. Arguments can be a mixture of BlobKey,
    BlobInfo and str or unicode instances, where in case of strings it should be either a string representation of
    BlobKey or a string representation of blob URI (see google.appengine.api.files.blobstore.get_file_name() function).

    :param args: One or more blob identifiers, which can be either BlobInfo, BlobKey, str or unicode objects. In case of
        str and unicode - it has to be a string representation of BlobKey or something I call blob url (Files API
        calls it blob filename - it's essentially a prefixed string representation of BlobKey: '/blobstore/<blob_key>').

    :param kwargs: Options for the behaviour of the function. Currently available options are:
        ignore_errors - should be boolean or anything that evaluates to boolean, when set to True - no exceptions will
            be raised by the function (default is False).
    """
    accepted_kwargs = ['ignore_errors']
    ignore_errors = kwargs.get('ignore_errors', False)
    if len(filter(lambda kwarg: kwarg not in accepted_kwargs, kwargs)) > 0 and not ignore_errors:
        raise NameError("Accepted keyword arguments are {0}".format(accepted_kwargs))

    if len(args) == 0 and not ignore_errors:
        raise ValueError("No arguments were given")

    blob_keys = []
    for arg in args:
        if isinstance(arg, blobstore.BlobKey):
            blob_keys.append(arg)
        elif isinstance(arg, blobstore.BlobInfo):
            blob_key = arg.key()
            blob_keys.append(blob_key)
        elif isinstance(arg, basestring):
            try:
                blob_key = files.blobstore.get_blob_key(arg)
                blob_keys.append(blob_key)
            except (files.InvalidArgumentError, files.InvalidFileNameError):
                # this could be non-existent key, but I don't think we can tell at this point
                # it is not worth to "verify" the key (by attempting to get BlobInfo), because
                # we're going to delete it anyway - so we're quietly accept this
                blob_key = blobstore.BlobKey(arg)
                blob_keys.append(blob_key)
        else:
            # unrecognized type
            if not ignore_errors:
                raise TypeError("All arguments must be instances of 'BlobInfo', 'BlobKey' or 'basestring', got '{0}' instead".format(type(arg).__name__))

    blob_keys_unique = set(blob_keys)
    blob_keys = list(blob_keys_unique)

    blobstore.delete(blob_keys=blob_keys)
