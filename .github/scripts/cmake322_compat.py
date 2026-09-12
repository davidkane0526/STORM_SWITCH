from pathlib import Path

path = Path("CMakeModules/CPMUtil.cmake")
text = path.read_text()

if text.count("return(PROPAGATE") != 3:
    raise SystemExit("Unexpected CPMUtil PROPAGATE layout; refusing to patch")

replacements = [
    (
        '''    set(${ARG_URL_OUT} "${url}")

    return(PROPAGATE ${ARG_URL_OUT} ${ARG_GIT_URL_OUT})
''',
        '''    set(${ARG_URL_OUT} "${url}" PARENT_SCOPE)
    if (DEFINED ARG_GIT_URL_OUT)
        set(${ARG_GIT_URL_OUT} "${${ARG_GIT_URL_OUT}}" PARENT_SCOPE)
    endif()
    return()
''',
    ),
    (
        '''    set(${out} ${CPM_SOURCE_CACHE}/${lower_name}/${key})

    return(PROPAGATE ${out})
''',
        '''    set(${out} ${CPM_SOURCE_CACHE}/${lower_name}/${key} PARENT_SCOPE)
    return()
''',
    ),
    (
        '''    file(REAL_PATH ${CPMUTIL_JSON_FILE} ${out})
    return(PROPAGATE ${out})
''',
        '''    file(REAL_PATH ${CPMUTIL_JSON_FILE} ${out})
    set(${out} "${${out}}" PARENT_SCOPE)
    return()
''',
    ),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f"Expected CPMUtil block not found:\n{old}")
    text = text.replace(old, new, 1)

if "return(PROPAGATE" in text:
    raise SystemExit("Unpatched return(PROPAGATE) remains")

path.write_text(text)
print("Patched all three CPMUtil return(PROPAGATE ...) sites for CMake 3.22")
