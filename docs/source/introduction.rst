What's prettyconf
-----------------

Prettyconf is a Python library created to make easy the separation of
configuration and code following the recomendations of `12 Factor`_'s topic
about configs.


Motivation
++++++++++

Configuration is just another API of you app, aimed for users who will install
and run it, allowing them to *preset* the state of a program, without having to
interact with it, only through static files or environment variables.

It is an important aspect of the architechture of any system, yet it is
sometimes overlooked.

It is important to provide a clear separation of configuration and code. This
is because config varies substantially across deploys and executions, code
should not. The same code can be run inside a container or in a regular
machine, it can be executed in production or in testing environments.

Well designed applications allow different ways to be configured. A proper
settings-discoverability chain goes as follows:

1. First CLI args are checked.
2. Then Environment variables.
3. Config files in different directories, that also imply some hierarchy. For
   example: config files in ``/etc/myapp/settings.ini`` are applied
   system-wide, while ``~/.config/myapp/settings.ini`` take precedence and are
   user-specific.
4. Hardcoded constants.

The rises the need to consolidate configuration in a single source of truth to
avoid having config management scattered all over the codebase.


.. _`12 Factor`: http://12factor.net/
