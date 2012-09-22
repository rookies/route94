# Find include file & library:
IF (UNIX)
	find_path(SFMLwindow_INCLUDE_DIR SFML/Window.hpp)
	find_library(SFMLwindow_LIBRARIES NAMES sfml-window)
ELSEIF (WIN32)
	set(SFMLwindow_INCLUDE_DIR ${CMAKE_SOURCE_DIR}/include/)
	set(SFMLwindow_LIBRARIES ${CMAKE_SOURCE_DIR}/sfml-window-2.dll)
ENDIF (UNIX)
# Set success status:
IF (SFMLwindow_LIBRARIES AND SFMLwindow_INCLUDE_DIR)
	set(SFMLwindow_FOUND "YES")
ELSE (SFMLwindow_LIBRARIES AND SFMLwindow_INCLUDE_DIR)
	set(SFMLwindow_FOUND "NO")
ENDIF (SFMLwindow_LIBRARIES AND SFMLwindow_INCLUDE_DIR)

IF (SFMLwindow_FOUND)
	IF (NOT SFMLwindow_FIND_QUIETLY)
		message(STATUS "Found SFMLwindow: ${SFMLwindow_LIBRARIES}")
	ENDIF (NOT SFMLwindow_FIND_QUIETLY)
ELSE (SFMLwindow_FOUND)
	IF (SFMLwindow_FIND_REQUIRED)
		message(FATAL_ERROR "Could not find SFMLwindow library")
	ENDIF (SFMLwindow_FIND_REQUIRED)
ENDIF (SFMLwindow_FOUND)

mark_as_advanced(SFMLwindow_LIBRARIES SFMLwindow_INCLUDE_DIR)