
import os
import glob

from terrareg.errors import TerraregError


class PathDoesNotExistError(TerraregError):
    """Path does not exist."""

    pass


class PathIsNotWithinBaseDirectoryError(TerraregError):
    """Sub path is not within base directory."""
    
    pass


def safe_join_paths(base_dir, *sub_paths, is_dir=False, is_file=False, allow_same_directory=False):
    """Combine base_dir and sub_path and ensure directory """

    # Ensure all of the sub_paths start with a relative path, if they start with a slash
    sub_paths = list(sub_paths)
    for itx, sub_path in enumerate(sub_paths):
        if sub_path.startswith('/'):
            sub_paths[itx] = '.{sub_path}'.format(sub_path=sub_paths[itx])

    joined_path = os.path.join(base_dir, *sub_paths)

    return check_subdirectory_within_base_dir(
        base_dir=base_dir, sub_dir=joined_path,
        is_dir=is_dir, is_file=is_file,
        allow_same_directory=allow_same_directory)

def safe_iglob(base_dir, pattern, recursive, is_file=False, is_dir=False):
    """Perform iglob, ensuring that each of the returned values is within the base directory."""
    results = []
    for res in glob.iglob('{base_dir}/{pattern}'.format(base_dir=base_dir, pattern=pattern),
                          recursive=recursive):
        results.append(check_subdirectory_within_base_dir(
            base_dir=base_dir, sub_dir=res,
            is_file=is_file, is_dir=is_dir
        ))
    return results

def check_subdirectory_within_base_dir(base_dir, sub_dir, is_dir=False, is_file=False, allow_same_directory=False):
    """
    Ensure directory is within base directory.
    Sub directory should be full paths - it should not be relative to the base_dir.

    Perform optional checks if sub_dir is a path or file.

    Return the real path of the sub directory.
    """

    if is_dir and is_file:
        raise Exception('Cannot expect object to be file and directory.')

    # Convert to real paths
    ## Since the base directory might not be a real path,
    ## convert it first
    real_base_path = os.path.realpath(base_dir)
    try:
        ## Convert sub-path to real path to compare
        real_sub_dir = os.path.realpath(sub_dir)
    except OSError:
        raise PathDoesNotExistError('File/directory does not exist')

    ## Ensure sub-path starts wtih base path.
    ## Append trailing slash to ensure, to avoid
    ## allowing /opt/test-this with a base directory of /opt/test
    ## If allowing the sub directory to match the base directory,
    ## optionally allow if real_sub_dir equals the base
    real_base_path_trailing_slash = '{0}/'.format(real_base_path) if real_base_path != '/' else real_base_path
    if (((not allow_same_directory or real_sub_dir != real_base_path) and
         not real_sub_dir.startswith(real_base_path_trailing_slash)) or
        (not allow_same_directory and real_sub_dir == real_base_path)):
        raise PathIsNotWithinBaseDirectoryError('Sub path is not within base directory')

    if is_dir:
        if not os.path.isdir(real_sub_dir):
            raise PathDoesNotExistError('Directory does not exist')
    if is_file:
        if not os.path.isfile(real_sub_dir):
            raise PathDoesNotExistError('File does not exist')

    # Return absolute path of joined paths
    return os.path.abspath(real_sub_dir)
