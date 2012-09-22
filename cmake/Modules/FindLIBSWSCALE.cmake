# Find include file & library:
IF (UNIX)
	find_path(LIBSWSCALE_INCLUDE_DIR libswscale/swscale.h)
	find_library(LIBSWSCALE_LIBRARIES NAMES swscale)
ELSEIF (WIN32)
	set(LIBSWSCALE_INCLUDE_DIR ${CMAKE_SOURCE_DIR}/include/)
	set(LIBSWSCALE_LIBRARIES ${CMAKE_SOURCE_DIR}/swscale-2.dll)
ENDIF (UNIX)
# Set success status:
IF (LIBSWSCALE_LIBRARIES AND LIBSWSCALE_INCLUDE_DIR)
	set(LIBSWSCALE_FOUND "YES")
ELSE (LIBSWSCALE_LIBRARIES AND LIBSWSCALE_INCLUDE_DIR)
	set(LIBSWSCALE_FOUND "NO")
ENDIF (LIBSWSCALE_LIBRARIES AND LIBSWSCALE_INCLUDE_DIR)

IF (LIBSWSCALE_FOUND)
	IF (NOT LIBSWSCALE_FIND_QUIETLY)
		message(STATUS "Found LIBSWSCALE: ${LIBSWSCALE_LIBRARIES}")
	ENDIF (NOT LIBSWSCALE_FIND_QUIETLY)
ELSE (LIBSWSCALE_FOUND)
	IF (LIBSWSCALE_FIND_REQUIRED)
		message(FATAL_ERROR "Could not find LIBSWSCALE library")
	ENDIF (LIBSWSCALE_FIND_REQUIRED)
ENDIF (LIBSWSCALE_FOUND)

mark_as_advanced(LIBSWSCALE_LIBRARIES LIBSWSCALE_INCLUDE_DIR)