"""Version handling."""

import collections
import re


class Version:
    """
    A semver compatible version class.

    :param major: version when you make incompatible API changes.
    :param minor: version when you add functionality in
                  a backwards-compatible manner.
    :param patch: version when you make backwards-compatible bug fixes.
    :param prerelease: an optional prerelease string
    :param build: an optional build string
    """

    __slots__ = ("_major", "_minor", "_patch", "_prerelease", "_build")
    #: Regex for number in a prerelease
    _LAST_NUMBER = re.compile(r"(?:[^\d]*(\d+)[^\d]*)+")
    #: Regex template for a semver version
    _REGEX_TEMPLATE = r"""
            ^
            (?P<major>0|[1-9]\d*)
            (?:
                \.
                (?P<minor>0|[1-9]\d*)
                (?:
                    \.
                    (?P<patch>0|[1-9]\d*)
                ){opt_patch}
            ){opt_minor}
            (?:-(?P<prerelease>
                (?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)
                (?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*
            ))?
            (?:\+(?P<build>
                [0-9a-zA-Z-]+
                (?:\.[0-9a-zA-Z-]+)*
            ))?
            $
        """
    #: Regex for a semver version
    _REGEX = re.compile(
        _REGEX_TEMPLATE.format(opt_patch="", opt_minor=""),
        re.VERBOSE,
    )
    #: Regex for a semver version that might be shorter
    _REGEX_OPTIONAL_MINOR_AND_PATCH = re.compile(
        _REGEX_TEMPLATE.format(opt_patch="?", opt_minor="?"),
        re.VERBOSE,
    )

    def __init__(
        self,
        major,
        minor=0,
        patch=0,
        prerelease=None,
        build=None,
    ):
        # Build a dictionary of the arguments except prerelease and build
        version_parts = {"major": int(major), "minor": int(minor), "patch": int(patch)}

        for name, value in version_parts.items():
            if value < 0:
                raise ValueError(
                    "{!r} is negative. A version can only be positive.".format(name)
                )

        self._major = version_parts["major"]
        self._minor = version_parts["minor"]
        self._patch = version_parts["patch"]
        self._prerelease = None if prerelease is None else str(prerelease)
        self._build = None if build is None else str(build)

    @property
    def major(self) -> int:
        """The major part of a version (read-only)."""
        return self._major

    @major.setter
    def major(self, value):
        raise AttributeError("attribute 'major' is readonly")

    @property
    def minor(self) -> int:
        """The minor part of a version (read-only)."""
        return self._minor

    @minor.setter
    def minor(self, value):
        raise AttributeError("attribute 'minor' is readonly")

    @property
    def patch(self) -> int:
        """The patch part of a version (read-only)."""
        return self._patch

    @patch.setter
    def patch(self, value):
        raise AttributeError("attribute 'patch' is readonly")

    @property
    def prerelease(self):
        """The prerelease part of a version (read-only)."""
        return self._prerelease

    @prerelease.setter
    def prerelease(self, value):
        raise AttributeError("attribute 'prerelease' is readonly")

    @property
    def build(self):
        """The build part of a version (read-only)."""
        return self._build

    @build.setter
    def build(self, value):
        raise AttributeError("attribute 'build' is readonly")

    def to_tuple(self):
        """
        Convert the Version object to a tuple.

        .. versionadded:: 2.10.0
           Renamed ``VersionInfo._astuple`` to ``VersionInfo.to_tuple`` to
           make this function available in the public API.

        :return: a tuple with all the parts

        >>> semver.Version(5, 3, 1).to_tuple()
        (5, 3, 1, None, None)
        """
        return (self.major, self.minor, self.patch, self.prerelease, self.build)

    def to_dict(self):
        """
        Convert the Version object to an OrderedDict.

        .. versionadded:: 2.10.0
           Renamed ``VersionInfo._asdict`` to ``VersionInfo.to_dict`` to
           make this function available in the public API.

        :return: an OrderedDict with the keys in the order ``major``, ``minor``,
          ``patch``, ``prerelease``, and ``build``.

        >>> semver.Version(3, 2, 1).to_dict()
        OrderedDict([('major', 3), ('minor', 2), ('patch', 1), \
('prerelease', None), ('build', None)])
        """
        return collections.OrderedDict(
            (
                ("major", self.major),
                ("minor", self.minor),
                ("patch", self.patch),
                ("prerelease", self.prerelease),
                ("build", self.build),
            )
        )

    def __iter__(self):
        """Return iter(self)."""
        yield from self.to_tuple()

    @staticmethod
    def _increment_string(string: str) -> str:
        """
        Look for the last sequence of number(s) in a string and increment.

        :param string: the string to search for.
        :return: the incremented string

        Source:
        http://code.activestate.com/recipes/442460-increment-numbers-in-a-string/#c1
        """
        match = Version._LAST_NUMBER.search(string)
        if match:
            next_ = str(int(match.group(1)) + 1)
            start, end = match.span(1)
            string = string[: max(end - len(next_), start)] + next_ + string[end:]
        return string

    def __eq__(self, other):  # type: ignore
        return self.compare(other) == 0

    def __ne__(self, other):  # type: ignore
        return self.compare(other) != 0

    def __lt__(self, other):
        return self.compare(other) < 0

    def __le__(self, other):
        return self.compare(other) <= 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __ge__(self, other):
        return self.compare(other) >= 0

    def __getitem__(self, index):
        """
        self.__getitem__(index) <==> self[index] Implement getitem.

        If the part  requested is undefined, or a part of the range requested
        is undefined, it will throw an index error.
        Negative indices are not supported.

        :param Union[int, slice] index: a positive integer indicating the
               offset or a :func:`slice` object
        :raises IndexError: if index is beyond the range or a part is None
        :return: the requested part of the version at position index

        >>> ver = semver.Version.parse("3.4.5")
        >>> ver[0], ver[1], ver[2]
        (3, 4, 5)
        """
        if isinstance(index, int):
            index = slice(index, index + 1)

        if (
            isinstance(index, slice)
            and (index.start is not None and index.start < 0)
            or (index.stop is not None and index.stop < 0)
        ):
            raise IndexError("Version index cannot be negative")

        part = tuple(filter(lambda p: p is not None, self.to_tuple()[index]))

        if len(part) == 1:
            return part[0]
        elif not part:
            raise IndexError("Version part undefined")
        return part

    def __repr__(self):
        s = ", ".join("%s=%r" % (key, val) for key, val in self.to_dict().items())
        return "%s(%s)" % (type(self).__name__, s)

    def __str__(self):
        version = "%d.%d.%d" % (self.major, self.minor, self.patch)
        if self.prerelease:
            version += "-%s" % self.prerelease
        if self.build:
            version += "+%s" % self.build
        return version

    def __hash__(self):
        return hash(self.to_tuple()[:4])

    def finalize_version(self):
        """
        Remove any prerelease and build metadata from the version.

        :return: a new instance with the finalized version string

        >>> str(semver.Version.parse('1.2.3-rc.5').finalize_version())
        '1.2.3'
        """
        cls = type(self)
        return cls(self.major, self.minor, self.patch)

    def match(self, match_expr) -> bool:
        """
        Compare self to match a match expression.

        :param match_expr: optional operator and version; valid operators are
              ``<```   smaller than
              ``>``   greater than
              ``>=``  greator or equal than
              ``<=``  smaller or equal than
              ``==``  equal
              ``!=``  not equal
        :return: True if the expression matches the version, otherwise False

        >>> semver.Version.parse("2.0.0").match(">=1.0.0")
        True
        >>> semver.Version.parse("1.0.0").match(">1.0.0")
        False
        >>> semver.Version.parse("4.0.4").match("4.0.4")
        True
        """
        prefix = match_expr[:2]
        if prefix in (">=", "<=", "==", "!="):
            match_version = match_expr[2:]
        elif prefix and prefix[0] in (">", "<"):
            prefix = prefix[0]
            match_version = match_expr[1:]
        elif match_expr and match_expr[0] in "0123456789":
            prefix = "=="
            match_version = match_expr
        else:
            raise ValueError(
                "match_expr parameter should be in format <op><ver>, "
                "where <op> is one of "
                "['<', '>', '==', '<=', '>=', '!=']. "
                "You provided: %r" % match_expr
            )

        possibilities_dict = {
            ">": (1,),
            "<": (-1,),
            "==": (0,),
            "!=": (-1, 1),
            ">=": (0, 1),
            "<=": (-1, 0),
        }

        possibilities = possibilities_dict[prefix]
        cmp_res = self.compare(match_version)

        return cmp_res in possibilities

    @classmethod
    def parse(cls, version, optional_minor_and_patch=False) -> "Version":
        """
        Parse version string to a Version instance.

        .. versionchanged:: 2.11.0
           Changed method from static to classmethod to
           allow subclasses.
        .. versionchanged:: 3.0.0
           Added optional parameter optional_minor_and_patch to allow optional
           minor and patch parts.

        :param version: version string
        :param optional_minor_and_patch: if set to true, the version string to parse \
           can contain optional minor and patch parts. Optional parts are set to zero.
           By default (False), the version string to parse has to follow the semver
           specification.
        :return: a new :class:`Version` instance
        :raises ValueError: if version is invalid
        :raises TypeError: if version contains the wrong type

        >>> semver.Version.parse('3.4.5-pre.2+build.4')
        Version(major=3, minor=4, patch=5, \
prerelease='pre.2', build='build.4')
        """
        if isinstance(version, bytes):
            version = version.decode("UTF-8")
        elif not isinstance(version, str):  # type: ignore
            raise TypeError("not expecting type '%s'" % type(version))

        if optional_minor_and_patch:
            match = cls._REGEX_OPTIONAL_MINOR_AND_PATCH.match(version)
        else:
            match = cls._REGEX.match(version)
        if match is None:
            raise ValueError(f"{version} is not valid SemVer string")

        matched_version_parts = match.groupdict()
        if not matched_version_parts["minor"]:
            matched_version_parts["minor"] = 0
        if not matched_version_parts["patch"]:
            matched_version_parts["patch"] = 0

        return cls(**matched_version_parts)

    def replace(self, **parts):
        """
        Replace one or more parts of a version and return a new
        :class:`Version` object, but leave self untouched

        .. versionadded:: 2.9.0
           Added :func:`Version.replace`

        :param parts: the parts to be updated. Valid keys are:
          ``major``, ``minor``, ``patch``, ``prerelease``, or ``build``
        :return: the new :class:`Version` object with the changed
          parts
        :raises TypeError: if ``parts`` contain invalid keys
        """
        version = self.to_dict()
        version.update(parts)
        try:
            return Version(**version)  # type: ignore
        except TypeError:
            unknownkeys = set(parts) - set(self.to_dict())
            error = "replace() got %d unexpected keyword argument(s): %s" % (
                len(unknownkeys),
                ", ".join(unknownkeys),
            )
            raise TypeError(error)

    @classmethod
    def isvalid(cls, version: str) -> bool:
        """
        Check if the string is a valid semver version.

        .. versionadded:: 2.9.1

        :param version: the version string to check
        :return: True if the version string is a valid semver version, False
                 otherwise.
        """
        try:
            cls.parse(version)
            return True
        except ValueError:
            return False
