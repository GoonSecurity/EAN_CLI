if [ "$#" -lt 1 ]; then
 echo "$0 <domain>";
 exit;
fi;
echo "Starting...";
rm /tmp/tmpeanoutput.txt;
assetfinder -subs-only $1 | xargs -L 1 echo https:// | tr -d " " | xargs -L 1 python3 ./tokens.py -t $1 -u | tee -a /tmp/tmpeanoutput.txt;
            
