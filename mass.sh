if [ "$#" -lt 1 ]; then
 echo "$0 <domain>";
 exit;
fi;
echo "Starting, this will take a while...";
rm /tmp/tmpeanoutput.txt;
assetfinder -subs-only $1 | sort -u | uniq | xargs -L 1 echo https:// | tr -d " " | xargs -L 1 -P 3 python3 ./tokens.py -t $1 -u | tee -a /tmp/tmpeanoutput.txt;
