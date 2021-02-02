###
 # \file
 #
 # \brief AT interface utilities
 #
 # (C) NimbeLink Corp. 2020
 #
 # All rights reserved except as explicitly granted in the license agreement
 # between NimbeLink Corp. and the designated licensee.  No other use or
 # disclosure of this software is permitted. Portions of this software may be
 # subject to third party license terms as specified in this software, and such
 # portions are excluded from the preceding copyright notice of NimbeLink Corp.
 ##

class Response(object):
    """A response to an AT command
    """

    class Result:
        """A result of an AT command
        """

        class Type:
            """Result types
            """

            Ok          = 1
            """A successful result"""

            Error       = 2
            """A generic error"""

            CmeError    = 3
            """A CME error"""

            CmsError    = 4
            """A CMS error"""

        def __init__(self, type, code = None):
            """Creates a new result

            :param self:
                Self
            :param type:
                The type of response this is
            :param code:
                An error code, if any

            :return none:
            """

            self.type = type
            self.code = code

        @staticmethod
        def makeFromString(string):
            """Makes a result from the result output

            This assumes there is only a single line, it's the last one, and
            all line endings and/or whitespace have been stripped.

            :param string:
                The string to parse

            :raise Exception:
                Failed to parse result

            :return Result:
                The result
            """

            # Assume this is a generic error with no error code
            type = Response.Result.Type.Error
            code = None

            # If the last line starts with 'CME', it's a CME error
            if string.startswith("+CME ERROR"):
                type = Response.Result.Type.CmeError

            # Else, if the last line starts with 'CMS', it's a CMS error
            elif string.startswith("+CMS ERROR"):
                type = Response.Result.Type.CmsError

            # Else, if the last line is the generic 'ERROR', it's an error
            elif string.startswith("ERROR"):
                type = Response.Result.Type.Error

            # Else, if the last line is 'OK', it's an Ok result
            elif string.strip() == "OK":
                type = Response.Result.Type.Ok

            # Else, we don't know how to parse this
            else:
                raise Exception("Failed to parse result string '{}'".format(string))

            # If this was an error that should contain a code, try parsing it
            if (type == Response.Result.Type.CmeError) or (type == Response.Result.Type.CmsError):
                try:
                    code = int(string.split(":").strip())
                except ValueError:
                    code = None

            return Response.Result(type = type, code = code)

    def __init__(self, output, result):
        """Creates a response

        :param self:
            Self
        :param output:
            An array of generic output lines, sans result
        :param result:
            The result of the response

        :return none:
        """

        self.output = output
        self.result = result

    @staticmethod
    def makeFromString(string):
        """Creates a new response from output

        :param string:
            The raw string output to parse

        :raise Exception:
            Failed to parse result

        :return none:
        """

        # Split the output into individual lines
        lines = string.replace("\r", "").split("\n")

        # Clear out any blank ones
        lines = [line for line in lines if len(line) > 0]

        # Split the lines into general output and the final result
        output = lines[:-1]
        result = lines[-1]

        # Make the result from the last line
        result = Response.Result.makeFromString(string = result)

        return Response(output = output, result = result)
