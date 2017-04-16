#!/usr/bin/env bash

outfile="run_search_out.txt"
if [ -f ${outfile} ]; then
    echo "Removing ${outfile}"
    rm ${outfile}
fi

# Air Cargo Problems 1-3
for p in 1 2 3; do
    # Search methods:
    # 1 - BFS
    # 2 - DFS
    # 3 - Greedy Best Firsth Search
    # 4 - A* with Ignore Preconditons heuristic
    # 5 - A* with Level Sum heuristic
    for s in 1 3 7 9 10; do
        python run_search.py -p $p -s $s >> ${outfile} 
    done
done
