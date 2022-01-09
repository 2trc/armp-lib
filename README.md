
# https://apple.stackexchange.com/questions/80611/merging-multiple-csv-files-without-merging-the-header
Merging csv files and output header once
awk '(NR == 1) || (FNR > 1)' file*.csv > bigfile.csv