#!/bin/bash
PROJECTNAME="route94"

build_default()
{
	## Create build directory:
	if [[ ! -d build ]]; then
		echo " ==> Creating build directory ..."
		mkdir build || exit 1
	fi
	## Change into build directory:
	cd build || exit 1
	## Run CMake:
	echo " ==> Running CMake ..."
	cmake .. || exit 1
	## Run make:
	echo " ==> Running make ..."
	make || exit 1
	## Create symlink:
	cd ..
	if [[ ! -e "$PROJECTNAME" ]]; then
		echo " ==> Creating symlink $PROJECTNAME -> build/$PROJECTNAME ..."
		ln -s build/$PROJECTNAME $PROJECTNAME || exit 1
	fi
}
build_clean()
{
	echo " ==> Removing build directory ..."
	rm -rf build
	echo " ==> Removing game symlink ..."
	rm -f $PROJECTNAME
}
build_mo()
{
	echo " ==> Compiling language files ..."
	## Change into locale directory:
	cd "`dirname '$0'`/locale"
	## Run through .po files:
	for langf in *.po; do
		## Get language name:
		lang=`echo $langf | cut -d'.' -f1`
		## Print status on console:
		echo -n "Compiling language file for [$lang]... "
		## Create directory "locale/$lang"
		if [[ ! -d "$lang" ]]; then
			mkdir "$lang" || exit 1
		fi
		## Create directory "locale/$lang/LC_MESSAGES"
		if [[ ! -d "$lang/LC_MESSAGES" ]]; then
			mkdir "$lang/LC_MESSAGES" || exit 1
		fi
		## Create .mo file:
		msgfmt -o "$lang/LC_MESSAGES/$PROJECTNAME.mo" "$langf"
		## Print status on console:
		if [[ $? -eq 0 ]]; then
			echo "[DONE]"
		else
			echo "[FAIL]"
		fi
	done
}
build_countlines()
{
	cd "`dirname $0`"
	## Count lines:
	LINES_CPP=`find ./src -type f -name "*.cpp" -exec cat {} + | wc -l`
	LINES_HPP=`find ./src -type f \( -name "*.hpp" -o -name "*.hpp.in" \) -exec cat {} + | wc -l`
	LINES_PO=`find ./locale -type f -name "*.po" -exec cat {} + | wc -l`
	LINES_SH=`find . -type f -name "*.sh" -exec cat {} + | wc -l`
	LINES_CMAKE=`find . -type f \( -name "*.cmake" -o -name "CMakeLists.txt" \) -exec cat {} + | wc -l`
	LINES_PYTHON=`find . -type f -name "*.py" -exec cat {} + | wc -l`
	LINES_CPPA=`expr $LINES_CPP + $LINES_HPP`
	LINES_ALL=`expr $LINES_CPP + $LINES_HPP + $LINES_PO + $LINES_SH + $LINES_CMAKE + $LINES_PYTHON`
	## Write to stdout:
	echo "C++ Source Files ..... $(printf '%5d' $LINES_CPP) lines ($(printf '%3d' $(expr $(expr $LINES_CPP \* 100) / $LINES_ALL))%)"
	echo "C++ Header Files ..... $(printf '%5d' $LINES_HPP) lines ($(printf '%3d' $(expr $(expr $LINES_HPP \* 100) / $LINES_ALL))%)"
	echo "C++ Stuff together ... $(printf '%5d' $LINES_CPPA) lines ($(printf '%3d' $(expr $(expr $LINES_CPPA \* 100) / $LINES_ALL))%)"
	echo "Language Files ....... $(printf '%5d' $LINES_PO) lines ($(printf '%3d' $(expr $(expr $LINES_PO \* 100) / $LINES_ALL))%)"
	echo "Shell Scripts ........ $(printf '%5d' $LINES_SH) lines ($(printf '%3d' $(expr $(expr $LINES_SH \* 100) / $LINES_ALL))%)"
	echo "CMake Files .......... $(printf '%5d' $LINES_CMAKE) lines ($(printf '%3d' $(expr $(expr $LINES_CMAKE \* 100) / $LINES_ALL))%)"
	echo "Python Files ......... $(printf '%5d' $LINES_PYTHON) lines ($(printf '%3d' $(expr $(expr $LINES_PYTHON \* 100) / $LINES_ALL))%)"
	echo ""
	echo "Everything ........... $(printf '%5d' $LINES_ALL) lines"
}
build_pot()
{
	cd "`dirname $0`"
	xgettext --language=C++ --keyword=_ --keyword=__ --output=- `find ./src -type f -name "*.cpp" | xargs`
}

case $1 in
	all)
		build_clean
		build_default
		build_mo
		;;
	update)
		build_default
		build_mo
		;;
	clean)
		build_clean
		;;
	mo)
		build_mo
		;;
	pot)
		build_pot
		;;
	build)
		build_default
		;;
	countlines)
		build_countlines
		;;
	*)
		echo "Usage: $0 {clean,build,mo,pot,countlines,all,update}"
		echo ""
		echo "  clean:      remove build directory and game symlink"
		echo "  build:      create build directory, run CMake, make and create game symlink"
		echo "  mo:         create *.mo language files"
		echo "  pot:        create *.pot language template (writes to stdout)"
		echo "  countlines: count source code lines"
		echo ""
		echo "  all         = clean+build+mo"
		echo "  update      = build+mo"
		;;
esac
