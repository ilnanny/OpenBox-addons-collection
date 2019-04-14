#!/bin/sh
OBLOGOUT_PATH=`dirname $0`
PYTHONPATH="$PYTHONPATH:$OBLOGOUT_PATH" python $OBLOGOUT_PATH/data/oblogout -l -v $*
